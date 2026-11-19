# TASKS.md: Product

## 1. Backlog Conventions

Slices are end-to-end and user-visible, ordered by dependency. Requirement IDs reference FEATURES.md (F-XX). Decision IDs reference DECISIONS.md; **no interview answers were recorded**, so all DEC references are `TBD` and any task depending on an unconfirmed decision is marked **BLOCKED**. Verification is by the stated method only; no task below is claimed complete.

| Field | Meaning |
|:---|:---|
| Source | F-XX (FEATURES.md), API §X (API.md) |
| Decisions | DEC-XXX or `TBD` |
| Blocked by | Task IDs that must land first |
| Verify | Concrete acceptance method |

---

## 2. Data & Export Foundation

### TASK-01 — Emit `realData.js` from CSV + artifacts
- **Objective:** Produce the single UI data source via the offline exporter.
- **Source:** API §3.1–3.5; PRD "Pipeline Data ke Frontend".
- **Decisions:** `TBD` (exporter CLI flags not confirmed).
- **Blocked by:** none.
- **Acceptance:** `python scripts/export_dashboard_data.py --horizons 1 3 6 --out frontend/src/data/realData.js` exits `0`; module exports `latestSnapshot`, `domainAnomalies`, `history`, `evaluation`; missing artifact exits `1` with `ARTIFACT_MISSING`; schema mismatch exits `2`.
- **Verify:** Run exporter; assert exit codes against a deliberately removed `metrics_horizon_3m.json`.

### TASK-02 — Loaders: metrics, predictions, history, manifest
- **Objective:** Implement `load_metrics(h)`, `load_predictions(h)`, `load_history()`, `load_manifest()`.
- **Source:** API §3.2–3.5.
- **Decisions:** `TBD`.
- **Blocked by:** TASK-01.
- **Acceptance:** `load_metrics(6).test.accuracy == 0.0`; `load_predictions(1)` returns 18 rows Jan 2024–Jun 2025; `load_history()` returns 114 rows with `split` in {train,val,test}; `load_manifest().best_validation_horizon_months == 1`.
- **Verify:** Unit tests asserting row counts and the documented h=6 failure value.

---

## 3. P0 UI Slices

### TASK-03 — ENSO Snapshot Header (F-01)
- **Objective:** Render latest ONI, phase, and date from `latestSnapshot`.
- **Source:** F-01; API §3.1.
- **Decisions:** `TBD` (phase boundary confirmed inclusive per F-01 edge case).
- **Blocked by:** TASK-01.
- **Acceptance:** Shows `ONI = −0,02 °C`, label `Netral`, caption "Data terakhir: Juni 2025 … bukan kondisi hari ini"; `aria-label="Fase ENSO: Netral"`; zero XHR/fetch on mount; missing `oni_anom` → `—` + "Data tidak tersedia".
- **Verify:** DevTools Network panel (zero requests); screen-reader label inspection; boundary test at ±0.5 → `Netral`.

### TASK-04 — Regional SST Anomaly Grid (F-02)
- **Objective:** Five domain cards from `domainAnomalies`.
- **Source:** F-02; PRD domain table.
- **Decisions:** `TBD`.
- **Blocked by:** TASK-01.
- **Acceptance:** All five domains render (Niño 3.4, Karimata, Makassar, Jawa, Maluku–Papua); each card shows "Anomali terhadap rata-rata bulan yang sama"; Makassar shows `+0,181 °C`; null value → `—` muted, not omitted.
- **Verify:** Snapshot test asserting five cards and captions; null-injection test.

### TASK-05 — Model Evaluation Panel (F-03)
- **Objective:** Per-horizon metrics, confusion matrices, persistence baseline.
- **Source:** F-03; API §2, §3.2–3.3.
- **Decisions:** `TBD`.
- **Blocked by:** TASK-02.
- **Acceptance:** 1m shows `71,4%` and RMSE `0,180 °C`; 3m footnote "Accuracy 100% semu — seluruh bulan uji Netral."; 6m shows `0%` + `Gagal` (not hidden); baseline table states "Model tidak mengalahkan persistence."; 1m confusion matrix matches `[[2,0,0],[2,5,0],[0,0,0]]` (5/7 correct); missing metrics → "Metrik tidak tersedia".
- **Verify:** Fixture-driven render tests per horizon; missing-artifact test.

### TASK-06 — Limitations & Provenance (F-05)
- **Objective:** Surface all six PRD limitations and data traceability.
- **Source:** F-05; PRD "Keterbatasan".
- **Decisions:** `TBD`.
- **Blocked by:** TASK-01.
- **Acceptance:** Lists: non-realtime (last Jun 2025), persistence beats model, MHW mostly zero, rain proxy only, h3/h6 unreliable, backend not implemented.
- **Verify:** Content assertion test against PRD limitation list.

---

## 4. P1 Slice

### TASK-07 — ONI Historical Archive (F-04)
- **Objective:** Recharts line of 114 ONI rows with test-period shading and ±0.5 reference lines.
- **Source:** F-04; API §3.4.
- **Decisions:** `TBD`.
- **Blocked by:** TASK-02.
- **Acceptance:** 114 points Jan 2016–Jun 2025; shaded Jan 2024–Jun 2025; reference lines at ±0.5; tooltip shows month, comma ONI, phase label.
- **Verify:** Chart data-length assertion; tooltip snapshot; accessible title/description present.

---

## 5. Operational

### TASK-08 — CI build gate (Vercel + GitHub Actions)
- **Objective:** Build fails if exporter or schema drifts.
- **Source:** PRD stack (Vercel + GitHub Actions); API §2 error codes.
- **Decisions:** `TBD` (deploy policy unconfirmed).
- **Blocked by:** TASK-01, TASK-02.
- **Acceptance:** CI runs exporter then `npm run build`; non-zero exporter exit fails pipeline; deploy to Vercel only on green.
- **Verify:** Deliberately break an artifact; confirm pipeline fails.

---

## 6. Out of Scope (Not Tasked)

Realtime NOAA feed, live inference, Leaflet map, Clerk-gated roles, PostgreSQL/Prisma runtime layer — all `TBD` per PRD "Pengembangan Lanjutan" and DATABASE.md §1; excluded from this backlog.

<!-- SDD_SOURCE_DOCS: api,database,decisions,design,features,prd -->
