# AGENTS.md

Lautan.id: an ENSO dashboard plus an academic ML pipeline. Python training lives at the repo root; the React dashboard is in `frontend/`. UI copy and most docs are Indonesian. `README.md` is ENSO science background, not setup instructions.

## Commands

```bash
pip install -r requirements.txt          # numpy<2 and zarr<3 pins are deliberate
python main.py                           # train 1/3/6-month horizons; rewrites model/ and reports/
python main.py --horizons 1              # subset; also shrinks reports/ to that subset
python src/ml/ensemble.py --horizon 1 --epochs 300 --output-dir model/enso_ensemble_1m
python src/rainfall_prepro.py            # must run before preprocessing
python src/preprocessing.py --overwrite  # rebuild dataset/climate_dataset.zarr
python src/verify_zarr.py                # check all Zarr groups
python scripts/export_dashboard_data.py  # CSV + model artifacts -> frontend/src/data/realData.js
cd frontend
npm install
npm run dev                              # Vite dev server
npm run build
npm run lint                             # oxlint
```

No Python test, lint, or typecheck setup exists. Verify with `reports/enso_metrics.csv`, `reports/*.json`, per-horizon `model/enso_ensemble_*/metrics_horizon_*.json`, and a frontend build.

## Pipeline and data invariants

- `main.py` -> `src/pipeline.py` -> `src/learning.py`, which subprocesses `src/ml/ensemble.py` per horizon, then writes `reports/`, `model/model_manifest.json`, `recent_model.pt`, and `best_model.pt`.
- Inputs are `dataset/{train,val,test}_features.csv` (Jan 2016-Jun 2025, 114 rows). Splits are fixed and chronological: train 2016-2021, val 2022-2023, test 2024-Jun 2025. Never shuffle/random-split or fit scalers on val/test.
- Each horizon is a separate model (`target_oni_lead_{1,3,6}m`, `target_phase_lead_{1,3,6}m`). Test predictions have 7 rows by design (18 test months - 12-month window + 1); this is not a bug.
- `main.py --prepare-data` invokes preprocessing without `--overwrite`, so it fails once `dataset/climate_dataset.zarr` exists. Rebuild directly with `src/preprocessing.py --overwrite`.
- `--prepare-data` does not run `src/rainfall_prepro.py`; run it first if monthly rainfall CSVs are missing.
- `src/preprocessing.py` intentionally skips `dataset/data_rainfall` and the per-year Selatan Jawa / Maluku Utara NetCDFs; the combined `sst_5_wilayah_2015_2025.nc` covers them but is gitignored (>100 MB).
- `src/ml/2lstm.py` starts with a digit, so normal `import` syntax cannot load it. It is loaded via `importlib.import_module("src.ml.2lstm")`; keep that pattern.
- `model/model_manifest.json` currently lists only horizon 1 although all three artifact directories exist. `scripts/export_dashboard_data.py` reads all three dirs directly.
- Run commands from the repo root; `src/ml/ensemble.py` inserts the root into `sys.path`.

## Frontend

- The live app is `frontend/index.html` -> `frontend/src/main.jsx`, a single large file with hand-built SVG charts and no chart library. It imports `frontend/src/data.js`.
- `frontend/src/App.jsx`, `src/pages/`, and `src/components/` are an older, unused parallel implementation importing `src/data/realData.js`. Editing them does not change the live app.
- `src/data.js` is produced by legacy `scripts/build_lautanid_data.py`, which hardcodes forecast and evaluation blocks. `scripts/export_dashboard_data.py` instead derives `src/data/realData.js` from the CSV and model artifacts. Do not hand-edit generated data or invent numbers.
- `src/data/climateData.js` is unused mock data. `frontend/README.md`, `DESIGN_STITCH.md`, and parts of `PRODUCT.md` describe the older component tree; trust `index.html`/`main.jsx` for what is live, and `PRODUCT.md`/`DESIGN_STITCH.md` for model facts and honesty rules.
- There are no network calls for data: the dashboard is static. The backend is unimplemented (`backend/` has only `Dockerfile` and `requirements.txt`; `backend/main.py`, `model/service.py`, and `frontend/Dockerfile` do not exist), so full `docker compose up` cannot build. PostgreSQL alone works: copy `.env.example` to `.env`, then `docker compose up -d postgres-db`; `init.sql` runs only on a fresh volume.
- Keep UI text in Indonesian with decimal commas and keep the honesty caveats visible: 1 month is the only usable horizon, the 3-month 100% test accuracy is a trivial all-Neutral prediction, 6 months fails, and persistence has lower MAE at every horizon.

## Other

- Root `eda.py` duplicates `src/etl.py`; the pipeline uses `src/etl.py`.
- `.github/workflows/astro.yml` is a stale Astro Pages template for an app that does not exist here; it is not valid CI for this repo.
