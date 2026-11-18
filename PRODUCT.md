# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Two audiences, deliberately balanced — the UI must stay uncluttered and "mudah dipahami" (easy to understand) for any visitor:

- **Grading audience:** the lecturer/examiner and fellow students of Proyek Sistem Cerdas (Applied Data Science, semester 5), evaluating rigor: honest data handling, methodology, model skill, and stated limitations.
- **General / interested visitors:** the app is shared publicly beyond the course (public link; the og-card is actively shared). A first-time visitor should grasp the current ENSO state and the model's real limits without domain expertise.

Success = honest, comprehensible communication of ENSO conditions and model evidence to both audiences. User's standing mandate: don't display unimportant things; nothing may be invented.

## Product Purpose

KMRV is a monitoring and evaluation dashboard for Indonesia's maritime climate, centered on the El Niño–Southern Oscillation. It shows the latest ONI, SOI, and DMI from the repo dataset, SST anomalies for five maritime domains (Niño 3.4 reference plus Karimata, Makassar, south of Java, Maluku–Papua), and the honest evaluation of a real Causal LSTM + LightGBM pipeline. It demonstrates, as a course project, a reproducible ML pipeline on public NOAA-era data — not an operational forecasting service, and not a replacement for BMKG.

## Positioning

Verified facts — from the dataset and artifacts in this repo (do not soften or inflate these):

- **Architecture:** a Causal LSTM (PyTorch, `src/ml/2lstm.py`: single-layer `nn.LSTM`, hidden 32, dropout 0.1, MSE loss, Adam, early stopping) forecasts the future **ONI** value; its forecast becomes a feature for a LightGBM phase classifier (`src/ml/lgbm.py`) predicting La Niña / Neutral / El Niño. Orchestrated by `src/ml/ensemble.py` with chronological splits, a 12-month input window, StandardScaler, and a seed-fixed retrain for production.
- **Dataset actually present:** `dataset/train_features.csv` (72 rows, 2016-01–2021-12), `val_features.csv` (24 rows, 2022-01–2023-12), `test_features.csv` (18 rows, 2024-01–2025-06). Combined: 114 monthly rows, **January 2016 – June 2025**.
- **Features:** `oni_anom`, `oni_total`, `soi`, `dmi`, Niño 3.4 SST anomaly + zonal gradient, regional SST anomalies (Karimata, Makassar, Java, Maluku), per-region `mhw_*` columns, rainfall proxies (`rain_malaysia`, `rain_hawaii`), seasonal sin/cos, ENSO coupling index, lags (1/2/3/6/12 m) and rolling features. Targets: `target_oni_lead_{1,3,6}m` and `target_phase_lead_{1,3,6}m`.
- **Latest observation (June 2025):** ONI −0,107 °C (Netral); SOI +0,097; DMI −0,477 °C; SST anomalies Niño 3.4 +0,688, Karimata +1,289, Makassar +0,995, Selatan Jawa +0,116, Maluku–Papua +0,644. All SST columns are anomalies, not absolute temperatures.
- **Artifacts exist** for horizons 1/3/6 months: `model/enso_ensemble_{1m,3m,6m}/` (LSTM `.pt`, LightGBM `.txt`, scalers, `metrics_horizon_*.json`, test predictions). `model/model_manifest.json` records **best validation horizon = 1 month**.
- **Verified skill:** 1m — validation accuracy 0,769, balanced 0,792, LSTM RMSE 1,175 °C; test accuracy 0,714, macro F1 0,417, RMSE 0,180 °C. 3m — validation accuracy 0,231, RMSE 1,257 °C; test accuracy 1,000 but all 7 test samples are Neutral (trivial single-class prediction). 6m — validation and test collapse. Skill is demonstrated at **1 month only**.
- **Baselines (computed from the same test predictions):** MAE KMRV vs persistence — 1m 0,172 vs 0,108; 3m 0,152 vs 0,098; 6m 0,197 vs 0,100. Persistence is more accurate; never present KMRV as beating it.
- **Data coverage limits:** MHW columns are mostly zero or constant, and the only rainfall columns are Malaysia/Hawaii proxies. Indonesian regional MHW events and a seasonal rainfall matrix are **not available** and are not displayed. The former `Dampak` page was removed for this reason.
- **No realtime feed and no future inference.** The frontend reads a generated module, `frontend/src/data/realData.js`, built by `scripts/export_dashboard_data.py` from `dataset/*_features.csv` and `model/`. The UI shows the dataset's last month, not today's conditions.

Differentiator a neighboring product could not truthfully copy: a validation-first Indonesian ENSO dashboard that publishes its own weak leads and the fact that persistence beats it, with provenance on every number.

## Operating Context

- Course project for **Sistem Cerdas**, semester 5, Applied Data Science.
- Data window actually stored in the repo: **January 2016 – June 2025**, monthly. Upstream sources used by the pipeline: NOAA OISST v2.1, NOAA CPC (ONI), PSL NOAA (SOI, DMI); BMKG is the acknowledged authority for official/operational validation.
- Dev: frontend `npm run dev` (Vite, React); regenerate dashboard data with `python scripts/export_dashboard_data.py`; model pipeline `python main.py --horizons 1 3 6`; PostgreSQL via docker compose for the planned backend.
- Backend is **planned, not implemented**: `backend/` contains only Dockerfile + requirements. The UI makes no network calls for data.

## Capabilities and Constraints

- Working now: React + Vite app — landing page plus dashboard pages `Ringkasan`, `PrakiraanENSO`, `Laut`. All displayed numbers come from `frontend/src/data/realData.js`, generated from the dataset and model artifacts.
- Real visuals: ONI time series 2016–2025 with test-window shading, SST anomaly time series per domain, world-map anomaly beacons, test-prediction chart (actual ONI vs LSTM), metric table per horizon.
- Reproducible training pipeline end-to-end in the repo (download/ETL → Zarr → features → train → metrics).
- Binding constraints: (a) Indonesian-first UI language; (b) **Rule of Honesty** — no simulated values, no future forecast presented as real, weak horizons labelled as such; (c) scope guardrails — no daily-weather prediction claims, no BMKG partnership implied.
- Undecided: whether to add a live NOAA feed behind a backend proxy; whether to retrain so 3/6-month leads earn skill; unifying RONI terminology if RONI data is added.

## Brand Commitments

- Name **KMRV** — confirmed a model name, not an acronym. Tagline: "Proyeksi ENSO Maritim Indonesia" (landing uses "ENSO Maritim Indonesia").
- Brand symbol: small wave/trace SVG (dashed horizon line + rising curve + dot) used in nav and footer lockups.
- All UI copy in Indonesian; Indonesian decimal commas (e.g., "−0,11 °C") are part of the incumbent voice.

## Evidence on Hand

- Real, with paths: `dataset/{train,val,test}_features.csv`; trained artifacts and metrics under `model/`; `scripts/export_dashboard_data.py`; generated `frontend/src/data/realData.js`; reproducible pipeline in `src/`; methodology in `README.md`; brand mark + `og-card` (`frontend/public/og-card.png`).
- Absences future work must not fabricate: no testimonials, press, external validation, or user research; no BMKG partnership; no realtime feed; no regional MHW or rainfall matrix; no multi-year deterministic predictions. Do not state "KMRV beats persistence" — it does not.

## Product Principles

1. **Honesty is the design.** Every number traces to a dataset column or artifact file; weak horizons and losing baselines are shown, not hidden.
2. **Ease of understanding wins.** Lead with the latest ONI and its phase; let detail live on the evaluation page.
3. **Traceable proof.** Each panel names its source file (`dataset/*_features.csv`, `metrics_horizon_*.json`, `test_predictions_horizon_*.csv`).
4. **Evidence, not promises.** Historical evaluation only; no future forecast while inference is not served.
5. **Indonesia-grounded.** Niño 3.4 as the index, Indonesian seas as the response domain it is evaluated against.

## Accessibility & Inclusion

Good practice only, no formal WCAG target committed: adequate text contrast, keyboard operability and visible focus, charts with accessible titles/descriptors, and never conveying El Niño/La Niña state by color alone.
