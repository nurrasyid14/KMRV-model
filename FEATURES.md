# FEATURES.md: Product

## 1. Feature Map & Scope

Lautan.id is a **static, data-snapshot SPA**. All UI values originate from `frontend/src/data/realData.js`, generated offline by `scripts/export_dashboard_data.py`. No runtime network calls for data. Feature scope is bounded by the PRD; deferred items (realtime NOAA feed, live inference, Leaflet map) are out of scope.

| ID | Module | Purpose | Priority |
|:---|:---|:---|:---|
| F-01 | ENSO Snapshot Header | Show latest ONI, phase, date | P0 |
| F-02 | Regional SST Anomaly Grid | Five maritime domains | P0 |
| F-03 | Model Evaluation Panel | Honest per-horizon metrics | P0 |
| F-04 | ONI Historical Archive | Jan 2016–Jun 2025 chart | P1 |
| F-05 | Limitations & Provenance | Traceability + disclaimers | P0 |

---

## 2. F-01 — ENSO Snapshot Header

**User story:** As a first-time visitor, I want to see the current ENSO phase and ONI value immediately, so I understand ocean conditions without domain expertise.

**Behavior**
- Renders the **last dataset row** (June 2025): `oni_anom`, `soi`, `dmi`, derived phase label.
- Phase classification (from `oni_anom`): La Niña `< −0.5`, Netral `−0.5…+0.5`, El Niño `> +0.5`.
- Values formatted with **Indonesian decimal comma** and `−` (U+2212) sign, monospaced font, unit `°C`.
- Phase conveyed by **label text + icon**, never color alone (accessibility).

**Acceptance criteria**
1. Header displays `ONI = −0,02 °C` and label `Netral` for the June 2025 snapshot.
2. Timestamp caption reads "Data terakhir: Juni 2025" and explicitly states "bukan kondisi hari ini".
3. No network request is issued on mount (verified via DevTools Network panel: zero XHR/fetch).
4. Screen reader announces phase via `aria-label="Fase ENSO: Netral"`.

**Edge cases**
- Missing `oni_anom` in `realData.js` → render `—` and caption "Data tidak tersedia"; do not fabricate a value.
- Value exactly `±0.5` → classify as `Netral` (boundary inclusive).

---

## 3. F-02 — Regional SST Anomaly Grid

**User story:** As a visitor, I want to compare SST anomalies across Indonesian seas and Niño 3.4 to see local response to ENSO.

**Behavior**
- Five cards: Niño 3.4, Selat Karimata, Selat Makassar, Selatan Jawa, Maluku–Papua.
- Each shows `sst_*` anomaly value, unit `°C`, and a per-domain caption noting it is an **anomaly vs. same-month climatology** (not absolute temperature).
- Static coordinate label per domain (from PRD domain table).

**Acceptance criteria**
1. All five domains render with values traceable to `sst_nino34`, `sst_karimata`, `sst_makassar`, `sst_jawa`, `sst_maluku` columns.
2. Caption "Anomali terhadap rata-rata bulan yang sama" present on every card.
3. Values use Indonesian comma notation (e.g., `+0,181 °C` for Makassar).

**Edge cases**
- Domain with null value → card shows `—` with muted state, not omitted.

---

## 4. F-03 — Model Evaluation Panel

**User story:** As an academic reviewer, I want per-horizon metrics including failed horizons, so I can assess model rigor honestly.

**Behavior**
- Three horizon sections (1m, 3m, 6m), each sourced from `metrics_horizon_{h}m.json`.
- Displays Accuracy, Balanced Accuracy, Macro F1, LSTM RMSE, and confusion matrix from `test_predictions_horizon_{h}m.csv`.
- **Persistence baseline comparison table** (MAE LSTM vs. MAE Persistence) rendered unconditionally.
- Horizon status badges: `1m → Andal`, `3m → Trivial majority class`, `6m → Gagal`.

**Acceptance criteria**
1. Horizon 1m shows test Accuracy `71,4%` and LSTM RMSE `0,180 °C`.
2. Horizon 3m displays footnote: "Accuracy 100% semu — seluruh bulan uji Netral."
3. Horizon 6m displays `0%` accuracy and label `Gagal` without hiding the section.
4. Baseline table shows all three horizons with LSTM MAE > Persistence MAE, explicitly stating "Model tidak mengalahkan persistence."
5. Confusion matrix cells for horizon 1m test = `[[?, ?], [?, ?]]` matching 5/7 correct (2 Netral→La Niña errors).

**Edge cases**
- Missing metrics file → section renders `TBD` state with "Metrik tidak tersedia"; never infers values.

---

## 5. F-04 — ONI Historical Archive

**User story:** As a visitor, I want to view the full ONI history with test-period annotation, so I can contextualize the latest snapshot.

**Behavior**
- Recharts line chart of `oni_anom` across 114 monthly rows (Jan 2016 – Jun 2025).
- Shaded region marks test period (Jan 2024 – Jun 2025).
- Horizontal reference lines at `±0.5` (phase thresholds).
- Tooltip shows month, ONI value (comma decimal), and phase label.

**Acceptance criteria**
1. Chart x-axis spans exactly 114 months; first tick `Jan 2016`, last `Jun 2025`.
2. Test-period shading aligns with Jan 2024 start.
3. Chart has accessible `title`/`desc` and keyboard-focusable tooltip.
4. Phase bands not distinguished by color alone (pattern or label).

**Edge cases**
- Empty data array → render empty-state message, not broken chart.

---

## 6. F-05 — Limitations & Provenance

**User story:** As any user, I want explicit limitations and data provenance, so I trust what the dashboard does and does not claim.

**Behavior**
- Persistent disclaimer: "Bukan layanan operasional; peringatan resmi adalah wewenang BMKG."
- Lists all six PRD limitations (non-realtime, persistence beats model, MHW columns mostly zero, rainfall proxies only, horizons 3/6 unreliable, backend not implemented).
- Provenance footer: dataset range, model name (**Causal LSTM + LightGBM Ensemble**), repo note (`KMRV-model` is repo name only).

**Acceptance criteria**
1. All six limitations render verbatim from PRD.
2. Disclaimer visible on every route (persistent footer or banner).
3. Model name shown as "Causal LSTM + LightGBM Ensemble" — never "KMRV".

**Edge cases**
- None; static content.

---

## 7. Cross-Cutting Rules

| Rule | Specification | Source |
|:---|:---|:---|
| Language | All UI text Bahasa Indonesia | PRD |
| Number format | Indonesian comma decimal, U+2212 minus | PRD |
| Data source | `realData.js` only; no fetch | PRD pipeline |
| Color | Primary `#00a3c4`; phase never color-only | PRD brand/a11y |
| Accessibility | Visible focus, chart titles, non-color phase cues | PRD |

## 8. Out of Scope (Deferred)

Realtime NOAA feed, live model inference, interactive Leaflet SST map, and retraining for horizon 3/6 skill are **not implemented** per PRD "Pengembangan Lanjutan". Marked `TBD` pending future decisions.

> Data schema: See DATABASE.md. API surface (if backend enabled): See API.md.