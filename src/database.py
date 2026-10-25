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
    tensors should remain in Zarr; these methods store their queryable records
    and model outputs in PostgreSQL.
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
    }
    _DATE_COLUMNS = {
        "oisst_daily_observations": "time_stamp",
        "climate_indices": "date",
        "mhw_predictions": "target_date",
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
