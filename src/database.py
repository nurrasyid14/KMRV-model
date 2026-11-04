"""PostgreSQL storage and analytics reads for the project tables."""

import os
from datetime import date, datetime
from typing import Any, Iterable, Mapping, Optional, Union

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import MetaData, Table, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.dialects.postgresql import insert

load_dotenv()

DatabaseRecord = Mapping[str, Any]
DateFilter = Optional[Union[date, datetime, str]]


class Database:
    """Store project records in PostgreSQL and load tables as pandas DataFrames.

    The tables must already exist, as created by ``init.sql``. Large gridded
    tensors should remain in Zarr; these methods store their queryable records,
    model outputs, and evaluation metrics in PostgreSQL.
    """

    _TABLE_COLUMNS = {
        "mhw_regions": {
            "region_name", "lat_min", "lat_max", "lon_min", "lon_max",
        },
        "oisst_daily_observations": {
            "time_stamp", "latitude", "longitude", "sst", "anom", "err", "ice",
        },
        "climate_indices": {"date", "enso_index", "iod_index"},
        "mhw_predictions": {
            "region_name", "target_date", "sst_anomaly", "enso_index",
            "iod_index", "mhw_category", "duration_days", "model_version",
        },
        "model_metrics": {
            "model_name", "target_variable", "region_name", "lead_horizon",
            "mae", "rmse", "r2_score", "accuracy", "f1_score", "roc_auc",
            "brier_score", "sample_size", "evaluated_at",
        },
    }
    _DATE_COLUMNS = {
        "oisst_daily_observations": "time_stamp",
        "climate_indices": "date",
        "mhw_predictions": "target_date",
        "model_metrics": "evaluated_at",
    }

    def __init__(self, database_url: Optional[str] = None):
        """Create a database connection using a URL or the ``DATABASE_URL`` env var."""
        resolved_url = database_url or os.getenv("DATABASE_URL")
        if not resolved_url:
            raise ValueError(
                "Database URL is required; pass database_url or set DATABASE_URL."
            )
        self.engine: Engine = create_engine(resolved_url, pool_pre_ping=True)

    def close(self) -> None:
        """Dispose of pooled database connections."""
        self.engine.dispose()

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()

    @staticmethod
    def _records(records: Union[pd.DataFrame, Iterable[DatabaseRecord]]) -> list[dict[str, Any]]:
        if isinstance(records, pd.DataFrame):
            clean_frame = records.astype(object).where(pd.notna(records), None)
            return clean_frame.to_dict(orient="records")
        return [dict(record) for record in records]

    def _store_records(
        self,
        table_name: str,
        records: Union[pd.DataFrame, Iterable[DatabaseRecord]],
        conflict_columns: tuple[str, ...] = (),
    ) -> int:
        if table_name not in self._TABLE_COLUMNS:
            raise ValueError(f"Unsupported table: {table_name}")

        rows = self._records(records)
        if not rows:
            return 0

        allowed_columns = self._TABLE_COLUMNS[table_name]
        expected_columns = set(rows[0])
        for row in rows:
            unknown_columns = row.keys() - allowed_columns
            if unknown_columns:
                raise ValueError(
                    f"Unsupported columns for {table_name}: "
                    f"{sorted(unknown_columns)}"
                )
            if not row:
                raise ValueError(f"Cannot insert an empty record into {table_name}.")
            if set(row) != expected_columns:
                raise ValueError(
                    f"All records for {table_name} must have the same columns."
                )
            if not set(conflict_columns).issubset(row):
                raise ValueError(
                    f"Conflict columns {conflict_columns} are required for {table_name}."
                )

        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=self.engine)
        inserted_count = 0

        with self.engine.begin() as connection:
            for offset in range(0, len(rows), 1000):
                batch = rows[offset : offset + 1000]
                statement = insert(table).values(batch)
                if conflict_columns:
                    update_values = {
                        column: getattr(statement.excluded, column)
                        for column in batch[0]
                        if column not in conflict_columns
                    }
                    if update_values:
                        statement = statement.on_conflict_do_update(
                            index_elements=list(conflict_columns),
                            set_=update_values,
                        )
                    else:
                        statement = statement.on_conflict_do_nothing(
                            index_elements=list(conflict_columns)
                        )
                result = connection.execute(statement)
                inserted_count += result.rowcount

        return inserted_count

    def store_regions(
        self, records: Union[pd.DataFrame, Iterable[DatabaseRecord]]
    ) -> int:
        """Insert region names and bounding boxes; ``region_id`` is generated."""
        return self._store_records("mhw_regions", records)

    def store_observations(
        self, records: Union[pd.DataFrame, Iterable[DatabaseRecord]]
    ) -> int:
        """Insert or update observations by timestamp and grid coordinates."""
        return self._store_records(
            "oisst_daily_observations",
            records,
            conflict_columns=("time_stamp", "latitude", "longitude"),
        )

    def store_climate_indices(
        self, records: Union[pd.DataFrame, Iterable[DatabaseRecord]]
    ) -> int:
        """Insert or update climate indices by date."""
        return self._store_records(
            "climate_indices", records, conflict_columns=("date",)
        )

    def store_predictions(
        self, records: Union[pd.DataFrame, Iterable[DatabaseRecord]]
    ) -> int:
        """Insert model predictions; ``prediction_id`` and ``predicted_at`` default."""
        return self._store_records("mhw_predictions", records)

    def store_metrics(
        self, records: Union[pd.DataFrame, Iterable[DatabaseRecord]]
    ) -> int:
        """Insert model evaluation metrics; ``metric_id`` and ``evaluated_at`` default."""
        return self._store_records("model_metrics", records)

    def fetch_table(
        self,
        table_name: str,
        start_date: DateFilter = None,
        end_date: DateFilter = None,
    ) -> pd.DataFrame:
        """Load a supported table, optionally limited to an inclusive date range."""
        if table_name not in self._TABLE_COLUMNS:
            raise ValueError(f"Unsupported table: {table_name}")
        if (start_date is not None or end_date is not None) and table_name not in self._DATE_COLUMNS:
            raise ValueError(f"Date filtering is not supported for {table_name}.")

        query = f'SELECT * FROM "{table_name}"'
        parameters: dict[str, Any] = {}
        date_column = self._DATE_COLUMNS.get(table_name)
        if date_column and (start_date is not None or end_date is not None):
            conditions = []
            if start_date is not None:
                conditions.append(f'"{date_column}" >= :start_date')
                parameters["start_date"] = start_date
            if end_date is not None:
                conditions.append(f'"{date_column}" <= :end_date')
                parameters["end_date"] = end_date
            query += " WHERE " + " AND ".join(conditions)

        with self.engine.connect() as connection:
            return pd.read_sql(text(query), connection, params=parameters)

    def init_schema(self) -> None:
        """Create project tables and indexes if they do not already exist."""
        ddl_statements = [
            # PostGIS extension (supported natively on Supabase)
            "CREATE EXTENSION IF NOT EXISTS postgis;",
            # 1. Wilayah Perairan
            """
            CREATE TABLE IF NOT EXISTS mhw_regions (
                region_id SERIAL PRIMARY KEY,
                region_name VARCHAR(100) NOT NULL,
                lat_min FLOAT NOT NULL,
                lat_max FLOAT NOT NULL,
                lon_min FLOAT NOT NULL,
                lon_max FLOAT NOT NULL,
                geom GEOMETRY(Polygon, 4326)
            );
            """,
            # 2. Observasi Harian
            """
            CREATE TABLE IF NOT EXISTS oisst_daily_observations (
                obs_id BIGSERIAL PRIMARY KEY,
                time_stamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                sst FLOAT,
                anom FLOAT,
                err FLOAT,
                ice FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT unique_obs_grid_time UNIQUE (time_stamp, latitude, longitude)
            );
            """,
            "CREATE INDEX IF NOT EXISTS idx_oisst_time_lat_lon ON oisst_daily_observations (time_stamp, latitude, longitude);",
            # 3. Indeks Iklim
            """
            CREATE TABLE IF NOT EXISTS climate_indices (
                index_id SERIAL PRIMARY KEY,
                date DATE UNIQUE NOT NULL,
                enso_index FLOAT NOT NULL,
                iod_index FLOAT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            # 4. Prediksi MHW
            """
            CREATE TABLE IF NOT EXISTS mhw_predictions (
                prediction_id BIGSERIAL PRIMARY KEY,
                region_name VARCHAR(100) NOT NULL,
                target_date DATE NOT NULL,
                sst_anomaly FLOAT NOT NULL,
                enso_index FLOAT NOT NULL,
                iod_index FLOAT NOT NULL,
                mhw_category VARCHAR(50) NOT NULL,
                duration_days INT,
                model_version VARCHAR(50) DEFAULT 'PyTorch-LSTM-v1.0',
                predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            "CREATE INDEX IF NOT EXISTS idx_mhw_pred_date_region ON mhw_predictions (target_date, region_name);",
            # 5. Metrik Evaluasi Model
            """
            CREATE TABLE IF NOT EXISTS model_metrics (
                metric_id BIGSERIAL PRIMARY KEY,
                model_name VARCHAR(100) NOT NULL,
                target_variable VARCHAR(100) NOT NULL,
                region_name VARCHAR(100),
                lead_horizon INT,
                mae FLOAT,
                rmse FLOAT,
                r2_score FLOAT,
                accuracy FLOAT,
                f1_score FLOAT,
                roc_auc FLOAT,
                brier_score FLOAT,
                sample_size INT,
                evaluated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            """,
            "CREATE INDEX IF NOT EXISTS idx_model_metrics_name_target ON model_metrics (model_name, target_variable, lead_horizon);",
        ]
        with self.engine.begin() as connection:
            for stmt in ddl_statements:
                try:
                    connection.execute(text(stmt))
                except Exception as e:
                    # In case of postgis permission nuances in certain cloud providers
                    if "postgis" in stmt.lower():
                        continue
                    raise

    def fetch_analytics_tables(
        self,
        start_date: DateFilter = None,
        end_date: DateFilter = None,
    ) -> dict[str, pd.DataFrame]:
        """Load all project tables for analytics, applying date limits where valid."""
        return {
            table_name: self.fetch_table(
                table_name,
                start_date=start_date if table_name in self._DATE_COLUMNS else None,
                end_date=end_date if table_name in self._DATE_COLUMNS else None,
            )
            for table_name in self._TABLE_COLUMNS
        }


if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("Database Connectivity & Schema Check")
    print("=" * 60)
    url = os.getenv("DATABASE_URL")
    if not url:
        print("[ERROR] DATABASE_URL tidak ditemukan di file .env")
        sys.exit(1)

    print(f"Connecting to: {url.split('@')[-1] if '@' in url else url}")
    try:
        db = Database()
        print("[OK] Engine terhubung!")
        print("Menginisialisasi tabel skema...")
        db.init_schema()
        print("[OK] Inisialisasi skema (mhw_regions, climate_indices, mhw_predictions, model_metrics) berhasil!")
        for tbl in db._TABLE_COLUMNS:
            try:
                df = db.fetch_table(tbl)
                print(f"  - Tabel '{tbl}': {len(df)} baris")
            except Exception as ex:
                print(f"  - Tabel '{tbl}': belum ada / error ({ex})")
        db.close()
        print("\nSemua pengujian database selesai.")
    except Exception as e:
        print(f"[FAIL] Gagal terhubung ke database: {e}")

