"""Export real dataset and model artifacts for the dashboard.

Observations come from dataset/features_master_unscaled.csv (physical units).
Model metrics and test predictions come from model/ artifacts.
Writes frontend/src/data/realData.js. No mock values.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "frontend" / "src" / "data" / "realData.js"
REGION_KEYS = {
    "nino34": "sst_nino34",
    "karimata": "sst_karimata",
    "makassar": "sst_makassar",
    "jawa": "sst_jawa",
    "maluku": "sst_maluku",
}


def phase(value: float) -> str:
    if value >= 0.5:
        return "El Nino"
    if value <= -0.5:
        return "La Nina"
    return "Netral"


def split_for(date: pd.Timestamp) -> str:
    if date < pd.Timestamp("2022-01-01"):
        return "train"
    if date < pd.Timestamp("2024-01-01"):
        return "val"
    return "test"


def main() -> None:
    master = pd.read_csv(ROOT / "dataset" / "features_master_unscaled.csv")
    master["time"] = pd.to_datetime(master["time"])
    master = master.sort_values("time").reset_index(drop=True)
    master["month"] = master["time"].dt.month

    # Anomaly relative to the same calendar month across 2016-2025.
    for key, column in REGION_KEYS.items():
        climatology = master.groupby("month")[column].transform("mean")
        master[f"anom_{key}"] = master[column] - climatology

    history = []
    for _, row in master.iterrows():
        history.append(
            {
                "date": row["time"].strftime("%Y-%m"),
                "oni": round(float(row["oni_anom"]), 3),
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

    counts = {
        "elNino": sum(1 for point in history if point["oni"] >= 0.5),
        "netral": sum(1 for point in history if -0.5 < point["oni"] < 0.5),
        "laNina": sum(1 for point in history if point["oni"] <= -0.5),
    }
    warmest = max(history, key=lambda point: point["oni"])
    coldest = min(history, key=lambda point: point["oni"])
    warmestRegion = max(regions, key=lambda region: region["anomaly"])

    metrics = {
        str(horizon): json.loads(
            (ROOT / "model" / f"enso_ensemble_{horizon}m" / f"metrics_horizon_{horizon}m.json").read_text(
                encoding="utf-8"
            )
        )
        for horizon in (1, 3, 6)
    }

    test_predictions = {}
    derived = {}
    for horizon in (1, 3, 6):
        predictions = pd.read_csv(
            ROOT / "model" / f"enso_ensemble_{horizon}m" / f"test_predictions_horizon_{horizon}m.csv"
        )
        actual = predictions[f"actual_oni_lead_{horizon}m"].to_numpy()
        forecast = predictions[f"lstm_oni_lead_{horizon}m"].to_numpy()
        derived[str(horizon)] = {
            "kmrvMae": round(float(abs(actual - forecast).mean()), 3),
            "persistenceMae": round(float(abs(actual[1:] - actual[:-1]).mean()), 3)
            if len(actual) > 1
            else None,
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

    manifest = json.loads((ROOT / "model" / "model_manifest.json").read_text(encoding="utf-8"))

    data = {
        "meta": {
            "datasetStart": history[0]["date"],
            "datasetEnd": latest["date"],
            "rows": len(history),
            "source": "dataset/features_master_unscaled.csv",
            "bestValidationHorizon": manifest.get("best_validation_horizon_months"),
            "phaseRule": "El Nino >= +0,5 C; La Nina <= -0,5 C; Netral di antaranya",
            "climatology": "Anomali SST = SST - rata-rata bulan yang sama (2016-2025)",
        },
        "latest": {
            **latest,
            "phase": phase(latest["oni"]),
            "previousDate": previous["date"],
            "deltaOni": round(latest["oni"] - previous["oni"], 3),
        },
        "history": history,
        "regions": regions,
        "facts": {
            "counts": counts,
            "warmestOni": {"value": warmest["oni"], "date": warmest["date"]},
            "coldestOni": {"value": coldest["oni"], "date": coldest["date"]},
            "warmestRegion": {
                "name": warmestRegion["name"],
                "anomaly": warmestRegion["anomaly"],
            },
        },
        "metrics": metrics,
        "derived": derived,
        "testPredictions": test_predictions,
    }

    text = "// Generated from dataset/features_master_unscaled.csv and model/ artifacts. Do not hand-edit.\n"
    text += "export const realData = " + json.dumps(data, indent=2) + ";\n\n"
    text += "export const meta = realData.meta;\n"
    text += "export const latest = realData.latest;\n"
    text += "export const history = realData.history;\n"
    text += "export const regions = realData.regions;\n"
    text += "export const facts = realData.facts;\n"
    text += "export const metrics = realData.metrics;\n"
    text += "export const derived = realData.derived;\n"
    text += "export const testPredictions = realData.testPredictions;\n"
    OUT.write_text(text, encoding="utf-8")

    print(f"wrote {OUT} ({len(history)} rows)")
    print(
        f"latest {latest['date']} ONI {latest['oni']} phase {phase(latest['oni'])} "
        f"SST Nino34 {latest['sst']['nino34']} anomaly {latest['sstAnom']['nino34']}"
    )


if __name__ == "__main__":
    main()
