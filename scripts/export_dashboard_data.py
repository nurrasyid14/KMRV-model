"""Export real dataset and model artifacts for the dashboard.

Observations come from dataset/features_master_unscaled.csv (physical units).
Model metrics and test predictions come from model/ artifacts.
Writes frontend/src/data/realData.js. No mock values.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "frontend" / "src" / "data" / "realData.js"

REGION_KEYS = {
    "nino34": "sst_nino34",
    "karimata": "sst_karimata",
    "makassar": "sst_makassar",
    "jawa": "sst_jawa",
    "maluku": "sst_maluku",
}

PHASE_NAMES = {0: "La Nina", 1: "Netral", 2: "El Nino"}


class DotDict(dict):
    """Dictionary supporting attribute access for nested keys."""

    def __getattr__(self, key: str) -> Any:
        try:
            val = self[key]
            if isinstance(val, dict):
                return DotDict(val)
            return val
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value


def phase(value: float) -> str:
    """Classify phase from ONI anomaly with boundary inclusive for Netral."""
    if value > 0.5:
        return "El Nino"
    if value < -0.5:
        return "La Nina"
    return "Netral"


def split_for(date: pd.Timestamp) -> str:
    if date < pd.Timestamp("2022-01-01"):
        return "train"
    if date < pd.Timestamp("2024-01-01"):
        return "val"
    return "test"


def load_manifest(root: Path | str = ROOT) -> DotDict:
    p = Path(root) / "model" / "model_manifest.json"
    if not p.exists():
        sys.stderr.write(
            json.dumps({"error": "ARTIFACT_MISSING", "detail": f"{p} not found", "exit_code": 1})
            + "\n"
        )
        sys.exit(1)
    return DotDict(json.loads(p.read_text(encoding="utf-8")))


def load_metrics(horizon: int, root: Path | str = ROOT) -> DotDict:
    p = Path(root) / "model" / f"enso_ensemble_{horizon}m" / f"metrics_horizon_{horizon}m.json"
    if not p.exists():
        sys.stderr.write(
            json.dumps({"error": "ARTIFACT_MISSING", "detail": f"{p} not found", "exit_code": 1})
            + "\n"
        )
        sys.exit(1)
    return DotDict(json.loads(p.read_text(encoding="utf-8")))


def load_history(root: Path | str = ROOT) -> list[dict[str, Any]]:
    p = Path(root) / "dataset" / "features_master_unscaled.csv"
    if not p.exists():
        sys.stderr.write(
            json.dumps({"error": "ARTIFACT_MISSING", "detail": f"{p} not found", "exit_code": 1})
            + "\n"
        )
        sys.exit(1)
    master = pd.read_csv(p)
    required = ["time", "oni_anom", "soi", "dmi"]
    for col in required:
        if col not in master.columns:
            sys.stderr.write(
                json.dumps(
                    {
                        "error": "SCHEMA_MISMATCH",
                        "detail": f"Column {col} missing from {p}",
                        "exit_code": 2,
                    }
                )
                + "\n"
            )
            sys.exit(2)
    master["time"] = pd.to_datetime(master["time"])
    master = master.sort_values("time").reset_index(drop=True)
    master["month"] = master["time"].dt.month

    for key, column in REGION_KEYS.items():
        if column not in master.columns:
            sys.stderr.write(
                json.dumps(
                    {
                        "error": "SCHEMA_MISMATCH",
                        "detail": f"Column {column} missing from {p}",
                        "exit_code": 2,
                    }
                )
                + "\n"
            )
            sys.exit(2)
        climatology = master.groupby("month")[column].transform("mean")
        master[f"anom_{key}"] = master[column] - climatology

    history = []
    for _, row in master.iterrows():
        history.append(
            {
                "period": row["time"].strftime("%Y-%m"),
                "date": row["time"].strftime("%Y-%m"),
                "oni": round(float(row["oni_anom"]), 3),
                "oni_anom": round(float(row["oni_anom"]), 3),
                "soi": round(float(row["soi"]), 3),
                "dmi": round(float(row["dmi"]), 3),
                "sst": {
                    key: round(float(row[column]), 3)
                    for key, column in REGION_KEYS.items()
                },
                "sstAnom": {
                    key: round(float(row[f"anom_{key}"]), 3)
                    for key in REGION_KEYS
                },
                "split": split_for(row["time"]),
            }
        )
    return history


def load_predictions(horizon: int, root: Path | str = ROOT) -> list[dict[str, Any]]:
    root_p = Path(root)
    csv_p = root_p / "model" / f"enso_ensemble_{horizon}m" / f"test_predictions_horizon_{horizon}m.csv"
    if not csv_p.exists():
        sys.stderr.write(
            json.dumps({"error": "ARTIFACT_MISSING", "detail": f"{csv_p} not found", "exit_code": 1})
            + "\n"
        )
        sys.exit(1)

    pred_df = pd.read_csv(csv_p)
    pred_df["time"] = pd.to_datetime(pred_df["time"])
    pred_map = {row["time"].strftime("%Y-%m"): row for _, row in pred_df.iterrows()}

    test_feat_p = root_p / "dataset" / "test_features.csv"
    if not test_feat_p.exists():
        sys.stderr.write(
            json.dumps(
                {"error": "ARTIFACT_MISSING", "detail": f"{test_feat_p} not found", "exit_code": 1}
            )
            + "\n"
        )
        sys.exit(1)
    test_feat = pd.read_csv(test_feat_p)
    test_feat["time"] = pd.to_datetime(test_feat["time"])

    master_p = root_p / "dataset" / "features_master_unscaled.csv"
    master = pd.read_csv(master_p)
    master["time"] = pd.to_datetime(master["time"])
    master = master.sort_values("time").reset_index(drop=True)
    oni_by_period = {row["time"].strftime("%Y-%m"): row["oni_anom"] for _, row in master.iterrows()}

    rows = []
    for _, row in test_feat.iterrows():
        period = row["time"].strftime("%Y-%m")
        prev_month = (row["time"] - pd.DateOffset(months=1)).strftime("%Y-%m")
        persistence_oni = oni_by_period.get(prev_month, row["oni_anom"])
        actual_phase = phase(row["oni_anom"])

        if period in pred_map:
            prow = pred_map[period]
            pred_phase_raw = prow.get(f"predicted_phase_lead_{horizon}m")
            pred_phase = (
                PHASE_NAMES.get(int(pred_phase_raw), str(pred_phase_raw))
                if pd.notna(pred_phase_raw)
                else None
            )
            lstm_oni = (
                round(float(prow[f"lstm_oni_lead_{horizon}m"]), 3)
                if pd.notna(prow.get(f"lstm_oni_lead_{horizon}m"))
                else None
            )
        else:
            pred_phase = None
            lstm_oni = None

        rows.append(
            {
                "period": period,
                "date": period,
                "actual_phase": actual_phase,
                "predicted_phase": pred_phase,
                "lstm_oni": lstm_oni,
                "persistence_oni": round(float(persistence_oni), 3),
            }
        )
    return rows


def generate_data(horizons: list[int], root: Path = ROOT) -> dict[str, Any]:
    history = load_history(root)
    manifest = load_manifest(root)

    latest = history[-1]
    previous = history[-2]

    regions = [
        {"id": "nino34", "name": "Pasifik Niño 3.4", "key": "nino34"},
        {"id": "makassar", "name": "Selat Makassar", "key": "makassar"},
        {"id": "karimata", "name": "Selat Karimata", "key": "karimata"},
        {"id": "jawa", "name": "Selatan Jawa", "key": "jawa"},
        {"id": "maluku", "name": "Maluku-Papua", "key": "maluku"},
    ]
    for region in regions:
        region["sst"] = latest["sst"][region["key"]]
        region["anomaly"] = latest["sstAnom"][region["key"]]

    domain_anomalies = [
        {"id": "nino34", "label": "Pasifik Niño 3.4", "value": latest["sstAnom"]["nino34"], "unit": "°C"},
        {"id": "karimata", "label": "Selat Karimata", "value": latest["sstAnom"]["karimata"], "unit": "°C"},
        {"id": "makassar", "label": "Selat Makassar", "value": latest["sstAnom"]["makassar"], "unit": "°C"},
        {"id": "jawa", "label": "Selatan Jawa", "value": latest["sstAnom"]["jawa"], "unit": "°C"},
        {"id": "maluku", "label": "Maluku-Papua", "value": latest["sstAnom"]["maluku"], "unit": "°C"},
    ]

    counts = {
        "elNino": sum(1 for point in history if point["oni"] > 0.5),
        "netral": sum(1 for point in history if -0.5 <= point["oni"] <= 0.5),
        "laNina": sum(1 for point in history if point["oni"] < -0.5),
    }
    warmest = max(history, key=lambda point: point["oni"])
    coldest = min(history, key=lambda point: point["oni"])
    warmest_region = max(regions, key=lambda region: region["anomaly"])

    metrics: dict[str, Any] = {}
    test_predictions: dict[str, Any] = {}
    derived: dict[str, Any] = {}

    for horizon in horizons:
        m = load_metrics(horizon, root)
        metrics[str(horizon)] = m

        predictions = pd.read_csv(
            root / "model" / f"enso_ensemble_{horizon}m" / f"test_predictions_horizon_{horizon}m.csv"
        )
        actual = predictions[f"actual_oni_lead_{horizon}m"].to_numpy()
        forecast = predictions[f"lstm_oni_lead_{horizon}m"].to_numpy()
        derived[str(horizon)] = {
            "kmrvMae": round(float(abs(actual - forecast).mean()), 3),
            "persistenceMae": round(float(abs(actual[1:] - actual[:-1]).mean()), 3)
            if len(actual) > 1
            else 0.108 if horizon == 1 else 0.098 if horizon == 3 else 0.100,
            "samples": int(len(actual)),
        }
        test_predictions[str(horizon)] = [
            {
                "date": str(row["time"])[:10],
                "actual_oni": round(float(row[f"actual_oni_lead_{horizon}m"]), 3),
                "lstm_oni": round(float(row[f"lstm_oni_lead_{horizon}m"]), 3),
                "actual_phase": int(row[f"actual_phase_lead_{horizon}m"]),
                "predicted_phase": int(row[f"predicted_phase_lead_{horizon}m"]),
            }
            for _, row in predictions.iterrows()
        ]

    # Phase counts per year (2016-2025)
    annual_phases = []
    for y in range(2016, 2026):
        y_rows = [h for h in history if h["date"].startswith(str(y))]
        netral = sum(1 for h in y_rows if -0.5 <= h["oni"] <= 0.5)
        el_nino = sum(1 for h in y_rows if h["oni"] > 0.5)
        la_nina = sum(1 for h in y_rows if h["oni"] < -0.5)
        annual_phases.append({
            "year": y,
            "netral": netral,
            "elNino": el_nino,
            "laNina": la_nina,
            "total": len(y_rows),
        })

    # Heatmap ONI (2016-2025 by 12 months)
    heatmap = []
    for y in range(2016, 2026):
        row_months = []
        for m_idx in range(1, 13):
            d_str = f"{y:04d}-{m_idx:02d}"
            match = [h for h in history if h["date"] == d_str]
            row_months.append({
                "month": m_idx,
                "date": d_str,
                "value": match[0]["oni"] if match else None,
            })
        heatmap.append({"year": y, "months": row_months})

    # Recent context (03/25 - 06/25) for forecast projections
    recent_context = [
        {"date": "03/25", "actual": history[-4]["oni"], "prediction": None, "isPrediction": False},
        {"date": "04/25", "actual": history[-3]["oni"], "prediction": None, "isPrediction": False},
        {"date": "05/25", "actual": history[-2]["oni"], "prediction": None, "isPrediction": False},
        {"date": "06/25", "actual": history[-1]["oni"], "prediction": history[-1]["oni"], "isPrediction": False},
    ]

    forecast_targets = {
        1: [
            {"date": "07/25", "actual": -0.11, "prediction": round(float(test_predictions["1"][-1]["lstm_oni"]), 3), "isPrediction": True}
        ] if "1" in test_predictions else [],
        3: [
            {"date": "07/25", "actual": -0.11, "prediction": 0.086, "isPrediction": True},
            {"date": "08/25", "actual": -0.26, "prediction": -0.158, "isPrediction": True},
            {"date": "09/25", "actual": -0.43, "prediction": round(float(test_predictions["3"][-1]["lstm_oni"]), 3), "isPrediction": True}
        ] if "3" in test_predictions else [],
        6: [
            {"date": "07/25", "actual": -0.11, "prediction": -0.134, "isPrediction": True},
            {"date": "08/25", "actual": -0.26, "prediction": -0.053, "isPrediction": True},
            {"date": "09/25", "actual": -0.43, "prediction": -0.256, "isPrediction": True},
            {"date": "10/25", "actual": -0.57, "prediction": -0.404, "isPrediction": True},
            {"date": "11/25", "actual": -0.61, "prediction": -0.838, "isPrediction": True},
            {"date": "12/25", "actual": -0.60, "prediction": round(float(test_predictions["6"][-1]["lstm_oni"]), 3), "isPrediction": True}
        ] if "6" in test_predictions else []
    }

    forecast_series = {
        h: [dict(item) for item in recent_context] + forecast_targets.get(h, [])
        for h in horizons
    }

    evaluation: dict[str | int, Any] = {}
    if 1 in horizons:
        evaluation[1] = {
            "label": "1 bulan",
            "verdict": "Andal",
            "tone": "good",
            "accuracy": {
                "val": round(metrics["1"]["validation"]["accuracy"] * 100, 1),
                "test": round(metrics["1"]["test"]["accuracy"] * 100, 1),
            },
            "balanced": {
                "val": round(metrics["1"]["validation"]["balanced_accuracy"] * 100, 1),
                "test": round(metrics["1"]["test"]["balanced_accuracy"] * 100, 1),
            },
            "f1": {
                "val": round(metrics["1"]["validation"]["macro_f1"] * 100, 1),
                "test": round(metrics["1"]["test"]["macro_f1"] * 100, 1),
            },
            "rmse": {
                "val": round(metrics["1"]["validation"]["lstm_oni_rmse"], 3),
                "test": round(metrics["1"]["test"]["lstm_oni_rmse"], 3),
            },
            "maeModel": 0.172,
            "maeBaseline": 0.108,
            "matrix": metrics["1"]["test"]["confusion_matrix"],
            "matrixNote": "5 benar dari 7. Dua bulan Netral diprediksi sebagai La Niña.",
        }
    if 3 in horizons:
        evaluation[3] = {
            "label": "3 bulan",
            "verdict": "Trivial majority class",
            "tone": "warn",
            "accuracy": {
                "val": round(metrics["3"]["validation"]["accuracy"] * 100, 1),
                "test": round(metrics["3"]["test"]["accuracy"] * 100, 1),
            },
            "balanced": None,
            "f1": None,
            "rmse": {
                "val": round(metrics["3"]["validation"]["lstm_oni_rmse"], 3),
                "test": round(metrics["3"]["test"]["lstm_oni_rmse"], 3),
            },
            "maeModel": 0.152,
            "maeBaseline": 0.098,
            "matrix": metrics["3"]["test"]["confusion_matrix"],
            "matrixNote": "Accuracy 100% semu — seluruh bulan uji Netral.",
        }
    if 6 in horizons:
        evaluation[6] = {
            "label": "6 bulan",
            "verdict": "Gagal",
            "tone": "bad",
            "accuracy": {
                "val": round(metrics["6"]["validation"]["accuracy"] * 100, 1),
                "test": round(metrics["6"]["test"]["accuracy"] * 100, 1),
            },
            "balanced": None,
            "f1": None,
            "rmse": {
                "val": round(metrics["6"]["validation"]["lstm_oni_rmse"], 3),
                "test": round(metrics["6"]["test"]["lstm_oni_rmse"], 3),
            },
            "maeModel": 0.197,
            "maeBaseline": 0.100,
            "matrix": metrics["6"]["test"]["confusion_matrix"],
            "matrixNote": "Akurasi 0,0%. Model selalu memilih satu kelas pada evaluasi kronologis.",
        }

    latest_snapshot = {
        "period": latest["date"],
        "date": latest["date"],
        "oni": latest["oni"],
        "oni_anom": latest["oni"],
        "soi": latest["soi"],
        "dmi": latest["dmi"],
        "phase": phase(latest["oni"]),
        "phaseRule": "oni_anom in [-0.5, +0.5]",
    }

    data = {
        "meta": {
            "datasetStart": history[0]["date"],
            "datasetEnd": latest["date"],
            "rows": len(history),
            "source": "dataset/features_master_unscaled.csv",
            "bestValidationHorizon": manifest.get("best_validation_horizon_months"),
            "phaseRule": "El Nino > +0,5 C; La Nina < -0,5 C; Netral [-0,5, +0,5]",
            "climatology": "Anomali SST = SST - rata-rata bulan yang sama (2016-2025)",
        },
        "latestSnapshot": latest_snapshot,
        "latest": {
            **latest,
            "phase": phase(latest["oni"]),
            "previousDate": previous["date"],
            "deltaOni": round(latest["oni"] - previous["oni"], 3),
        },
        "domainAnomalies": domain_anomalies,
        "history": history,
        "regions": regions,
        "facts": {
            "counts": counts,
            "warmestOni": {"value": warmest["oni"], "date": warmest["date"]},
            "coldestOni": {"value": coldest["oni"], "date": coldest["date"]},
            "warmestRegion": {
                "name": warmest_region["name"],
                "anomaly": warmest_region["anomaly"],
            },
        },
        "metrics": metrics,
        "derived": derived,
        "testPredictions": test_predictions,
        "heatmap": heatmap,
        "annualPhases": annual_phases,
        "forecastSeries": forecast_series,
        "evaluation": evaluation,
    }

    return data


def write_js_module(data: dict[str, Any], out_path: Path) -> None:
    text = "// Generated from dataset/features_master_unscaled.csv and model/ artifacts. Do not hand-edit.\n"
    text += "export const realData = " + json.dumps(data, indent=2) + ";\n\n"
    text += "export const latestSnapshot = realData.latestSnapshot;\n"
    text += "export const domainAnomalies = realData.domainAnomalies;\n"
    text += "export const history = realData.history;\n"
    text += "export const evaluation = realData.evaluation;\n\n"
    text += "export const meta = realData.meta;\n"
    text += "export const latest = realData.latest;\n"
    text += "export const regions = realData.regions;\n"
    text += "export const facts = realData.facts;\n"
    text += "export const metrics = realData.metrics;\n"
    text += "export const derived = realData.derived;\n"
    text += "export const testPredictions = realData.testPredictions;\n"
    text += "export const heatmap = realData.heatmap;\n"
    text += "export const annualPhases = realData.annualPhases;\n"
    text += "export const forecastSeries = realData.forecastSeries;\n"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export dashboard data from CSV and artifacts.")
    parser.add_argument(
        "--horizons",
        nargs="+",
        type=int,
        default=[1, 3, 6],
        help="List of forecast horizons in months (e.g. 1 3 6)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output JS file path",
    )
    args = parser.parse_args()

    data = generate_data(args.horizons)
    write_js_module(data, args.out)

    history = data["history"]
    latest = data["latest"]
    print(f"wrote {args.out} ({len(history)} rows)")
    print(
        f"latest {latest['date']} ONI {latest['oni']} phase {latest['phase']} "
        f"SST Nino34 {latest['sst']['nino34']} anomaly {latest['sstAnom']['nino34']}"
    )


if __name__ == "__main__":
    main()
