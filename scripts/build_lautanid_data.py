import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "frontend" / "src" / "data.js"

master = pd.read_csv(ROOT / "dataset" / "features_master_unscaled.csv")
master["time"] = pd.to_datetime(master["time"])
master = master.sort_values("time").reset_index(drop=True)
master["month"] = master["time"].dt.month

region_keys = {
    "nino34": "sst_nino34",
    "karimata": "sst_karimata",
    "makassar": "sst_makassar",
    "jawa": "sst_jawa",
    "maluku": "sst_maluku",
}

for key, col in region_keys.items():
    clim = master.groupby("month")[col].transform("mean")
    master[f"anom_{key}"] = master[col] - clim

oni_archive = []
for _, row in master.iterrows():
    t = row["time"]
    split = "train" if t < pd.Timestamp("2022-01-01") else ("val" if t < pd.Timestamp("2024-01-01") else "test")
    oni_archive.append({
        "date": t.strftime("%Y-%m"),
        "value": round(float(row["oni_anom"]), 2),
        "split": split
    })

forecast_series = {}
for h in (1, 3, 6):
    preds = pd.read_csv(ROOT / "model" / f"enso_ensemble_{h}m" / f"test_predictions_horizon_{h}m.csv")
    preds["time"] = pd.to_datetime(preds["time"]).dt.strftime("%Y-%m")
    pred_map = dict(zip(preds["time"], preds[f"lstm_oni_lead_{h}m"]))
    
    series = []
    for _, row in master.iterrows():
        ym = row["time"].strftime("%Y-%m")
        act = round(float(row["oni_anom"]), 2)
        p_val = pred_map.get(ym)
        series.append({
            "date": ym,
            "actual": act,
            "prediction": round(float(p_val), 3) if p_val is not None else None
        })
    forecast_series[h] = series

last = master.iloc[-1]

latest = {
    "date": "Juni 2025",
    "oni": round(float(last["oni_anom"]), 2),
    "phase": "Netral",
    "soi": round(float(last["soi"]), 3),
    "dmi": round(float(last["dmi"]), 3),
    "note": "ONI berada di antara −0,5 dan +0,5 sehingga diklasifikasikan sebagai Netral."
}

sst_domains = [
    {
        "name": "Niño 3.4",
        "short": "N3.4",
        "value": round(float(last["anom_nino34"]), 3),
        "role": "Referensi indeks ENSO utama",
        "status": "Sedikit dingin"
    },
    {
        "name": "Selat Karimata",
        "short": "KRM",
        "value": round(float(last["anom_karimata"]), 3),
        "role": "Respons lokal Indonesia",
        "status": "Sedikit hangat"
    },
    {
        "name": "Selat Makassar",
        "short": "MKS",
        "value": round(float(last["anom_makassar"]), 3),
        "role": "Respons lokal Indonesia",
        "status": "Sedikit hangat"
    },
    {
        "name": "Selatan Jawa",
        "short": "JWA",
        "value": round(float(last["anom_jawa"]), 3),
        "role": "Respons lokal Indonesia",
        "status": "Sedikit hangat"
    },
    {
        "name": "Maluku–Papua",
        "short": "MLP",
        "value": round(float(last["anom_maluku"]), 3),
        "role": "Respons lokal Indonesia",
        "status": "Sedikit hangat"
    }
]

evaluation = {
    1: {
        "label": "1 bulan",
        "verdict": "Relatif andal",
        "tone": "good",
        "accuracy": {"val": 76.9, "test": 71.4},
        "balanced": {"val": 79.2, "test": 71.4},
        "f1": {"val": 66.8, "test": 41.7},
        "rmse": {"val": 1.175, "test": 0.180},
        "maeModel": 0.172,
        "maeBaseline": 0.108,
        "matrix": [[0, 0, 0], [2, 5, 0], [0, 0, 0]],
        "matrixNote": "5 benar dari 7. Dua bulan Netral diprediksi sebagai La Niña."
    },
    3: {
        "label": "3 bulan",
        "verdict": "Akurasi semu",
        "tone": "warn",
        "accuracy": {"val": 23.1, "test": 100.0},
        "balanced": None,
        "f1": None,
        "rmse": {"val": 1.257, "test": 0.174},
        "maeModel": 0.152,
        "maeBaseline": 0.098,
        "matrix": [[0, 0, 0], [0, 7, 0], [0, 0, 0]],
        "matrixNote": "Seluruh 7 bulan uji Netral; model menebak Netral semua. Bukan skill prediktif nyata."
    },
    6: {
        "label": "6 bulan",
        "verdict": "Tidak andal",
        "tone": "bad",
        "accuracy": {"val": 0.0, "test": 0.0},
        "balanced": None,
        "f1": None,
        "rmse": {"val": 1.258, "test": 0.217},
        "maeModel": 0.197,
        "maeBaseline": 0.100,
        "matrix": [[0, 0, 3], [0, 0, 4], [0, 0, 0]],
        "matrixNote": "Model selalu menebak satu kelas (El Niño). Prediksi tidak dapat diandalkan."
    }
}

split_meta = [
    {"label": "Train", "range": "Jan 2016 — Des 2021", "count": 72, "tone": "teal"},
    {"label": "Validasi", "range": "Jan 2022 — Des 2023", "count": 24, "tone": "amber"},
    {"label": "Uji", "range": "Jan 2024 — Jun 2025", "count": 18, "tone": "coral"}
]

content = f"""export const latest = {json.dumps(latest, indent=2)};

export const sstDomains = {json.dumps(sst_domains, indent=2)};

export const oniArchive = {json.dumps(oni_archive, indent=2)};

export const forecastSeries = {json.dumps(forecast_series, indent=2)};

export const evaluation = {json.dumps(evaluation, indent=2)};

export const splitMeta = {json.dumps(split_meta, indent=2)};
"""

OUT.write_text(content, encoding="utf-8")
print(f"Generated {OUT} successfully!")
