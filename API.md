# API.md: Product

## 1. Authentication & Authorization

Lautan.id is a **static SPA**. Per PRD "Pipeline Data ke Frontend", the UI performs **no network calls for data**; all values are baked into `frontend/src/data/realData.js` at build time. Consequently there is **no runtime data API** for the dashboard itself.

The only HTTP surface is the **offline export contract** between the Python pipeline and the frontend build. It is not a served API — it is a file-generation job. Clerk Auth v6 is present in the stack but **no role or protected workflow is defined** (see DESIGN.md §1, marked `TBD`). No endpoint below requires authentication.

| Concern | Value |
|:---|:---|
| Auth method | None (static SPA); Clerk present but unused — `TBD` |
| Header format | N/A |
| Transport | N/A at runtime; artifact export is filesystem-only |

---

## 2. Standard Response & Pagination Formats

Because there is no served API, "responses" are the **JSON/metrics artifacts** consumed by the export script. Success is a written file; error is a non-zero exit with stderr. Pagination does not apply — datasets are fixed-size (114 rows).

**Artifact envelope (all `metrics_horizon_{h}m.json`):**
```json
{
  "horizon_months": 1,
  "validation": { "accuracy": 0.769, "balanced_accuracy": 0.792, "macro_f1": 0.668, "lstm_rmse": 1.175 },
  "test":       { "accuracy": 0.714, "balanced_accuracy": 0.714, "macro_f1": 0.417, "lstm_rmse": 0.180 },
  "confusion_matrix_test": [[2,0,0],[2,5,0],[0,0,0]],
  "class_order": ["La Nina", "Netral", "El Nino"]
}
```

**Error format (exporter):**
```json
{ "error": "ARTIFACT_MISSING", "detail": "model/enso_ensemble_3m/metrics_horizon_3m.json not found", "exit_code": 1 }
```

---

## 3. API Endpoints (Export Contract)

These are the **five essential operations** of `scripts/export_dashboard_data.py` and the read-only artifact contracts they fulfill. Paths are filesystem artifacts, not HTTP routes.

### 3.1 `export_dashboard_data` — Generate `realData.js`

| Field | Value |
|:---|:---|
| Method | CLI invocation (`python scripts/export_dashboard_data.py`) |
| Path | `dataset/*_features.csv` + `model/enso_ensemble_*/` → `frontend/src/data/realData.js` |
| Description | Single source of truth for all UI data. Reads master CSV + per-horizon artifacts, emits one ES module. |
| Auth | None |
| Request | `--horizons 1 3 6 --out frontend/src/data/realData.js` |
| Response | ES module exporting `latestSnapshot`, `domainAnomalies`, `history`, `evaluation` |
| Status | `0` success; `1` artifact missing; `2` schema mismatch |

**Emitted shape (excerpt):**
```js
export const latestSnapshot = {
  period: "2025-06", oni: -0.02, soi: 0.097, dmi: -0.477,
  phase: "Netral", phaseRule: "oni_anom in [-0.5, +0.5]"
};
export const domainAnomalies = [
  { id: "nino34",    label: "Pasifik Niño 3.4", value: -0.119, unit: "°C" },
  { id: "makassar",  label: "Selat Makassar",   value:  0.181, unit: "°C" },
  { id: "jawa",      label: "Selatan Jawa",     value:  0.262, unit: "°C" }
  // karimata, maluku — same shape
];
```

### 3.2 `read_metrics` — Per-Horizon Metrics Loader

| Field | Value |
|:---|:---|
| Method | Function `load_metrics(horizon: int)` |
| Path | `model/enso_ensemble_{h}m/metrics_horizon_{h}m.json` |
| Description | Returns validation + test block for one horizon. Drives F-03 evaluation panel. |
| Auth | None |
| Request | `{ "horizon": 6 }` |
| Response | Envelope from §2; `test.accuracy = 0.0` for h=6 (documented failure) |
| Status | `200`-equivalent success; `404`-equivalent `ARTIFACT_MISSING` |

### 3.3 `read_predictions` — Test Predictions Loader

| Field | Value |
|:---|:---|
| Method | Function `load_predictions(horizon: int)` |
| Path | `model/enso_ensemble_{h}m/test_predictions_horizon_{h}m.csv` |
| Description | Returns 18 test rows (Jan 2024–Jun 2025) with `actual_phase`, `predicted_phase`, `lstm_oni`, `persistence_oni`. |
| Auth | None |
| Request | `{ "horizon": 1 }` |
| Response | `[{ "period": "2024-01", "actual_phase": "Netral", "predicted_phase": "La Nina", "lstm_oni": 0.12, "persistence_oni": 0.08 }]` (18 rows) |
| Status | Success; `ARTIFACT_MISSING` on absent CSV |

### 3.4 `read_history` — ONI Historical Archive

| Field | Value |
|:---|:---|
| Method | Function `load_history()` |
| Path | `dataset/features_master_unscaled.csv` |
| Description | Returns 114 monthly rows (Jan 2016–Jun 2025) of `period`, `oni_anom`, `split` (`train`/`val`/`test`) for F-04 archive chart. |
| Auth | None |
| Request | none |
| Response | `[{ "period": "2016-01", "oni_anom": 2.6, "split": "train" }, …]` |
| Status | Success; `SCHEMA_MISMATCH` if required columns absent |

### 3.5 `read_manifest` — Model Manifest

| Field | Value |
|:---|:---|
| Method | Function `load_manifest()` |
| Path | `model/model_manifest.json` |
| Description | Returns `best_validation_horizon_months` (=1) and artifact inventory; UI uses it to mark the reliable horizon. |
| Auth | None |
| Request | none |
| Response | `{ "best_validation_horizon_months": 1, "horizons": [1,3,6], "seed": 42 }` |
| Status | Success; `ARTIFACT_MISSING` |

> **Scope note:** Realtime NOAA ingestion and live inference are explicitly **not implemented** (PRD "Pengembangan Lanjutan"). Any future HTTP API for those is `TBD` and must not be assumed by these specs. All endpoints above are offline build-time contracts; no runtime fetch exists in the SPA.