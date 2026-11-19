# KMRV — Google Stitch Design Overview

Source of truth: `PRODUCT.md`, `frontend/src/tokens.css`, `src/ml/2lstm.py`,
`src/ml/lgbm.py`, `src/ml/ensemble.py`, `model/model_manifest.json`,
`model/enso_ensemble_{1,3,6}m/metrics_horizon_*.json`.

Use this document as the **project overview / master prompt** in Google Stitch.
Paste one screen prompt (Section 6) per Stitch frame. Every model fact below is
copied from the trained artifacts in this repo — Stitch must not add, rename, or
invent a model, dataset, or metric.

---

## 1. Product overview (paste into Stitch "Project overview")

> **KMRV** is a monitoring and inference dashboard for Indonesia's maritime
> climate, centered on the El Niño–Southern Oscillation (ENSO). It presents
> probabilistic El Niño / Neutral / La Niña outlooks at 1-, 3- and 6-month lead
> times, sea-surface temperature (SST) telemetry for five maritime domains,
> marine heatwave (MHW) status, and a seasonal regional rainfall-response
> matrix for Indonesia.
>
> **Audience:** (1) a university examiner grading rigor for *Sistem Cerdas*
> semester 5, and (2) a general first-time visitor following a public link.
> The design must be calm, uncluttered, and understandable without domain
> expertise. Indonesian-first copy; every number carries provenance or a
> "simulated" label.
>
> **Tone:** scientific, honest, quiet confidence. This is an instrument panel,
> not a marketing landing page. Never dress a weak forecast as a strong one.
>
> **Product language:** web dashboard, light theme, React-style component
> layout, desktop-first (1280–1440px) with a usable tablet layout.

---

## 2. Real model card (DO NOT ALTER)

These are the only model facts the UI may show. They come from the trained
pipeline in this repo.

**Model name:** KMRV ENSO ensemble — `causal_lstm_lightgbm`.

| Component | Exact specification |
| --- | --- |
| Stage 1 — forecaster | `CausalLSTM` (PyTorch): 1-layer `nn.LSTM`, hidden size **32**, dropout **0.1**, `Linear(32 → 1)`, MSE loss, Adam (lr **0.003**), batch **16**, up to **300** epochs, early stopping at **30** stale epochs, seed **42**. Predicts the future **ONI** value. |
| Input | **12-month** lookback window of standardized climate features (chronological split, `StandardScaler` fit on train only). |
| Stage 2 — classifier | **LightGBM** multiclass (3 classes: La Niña = 0, Neutral = 1, El Niño = 2), `n_estimators=300`, lr **0.03**, `num_leaves=7`, `max_depth=3`, `min_child_samples=5`, subsample **0.8**, colsample **0.8**, `reg_lambda=1.0`, early stopping 50, seed 42. Consumes the LSTM's ONI forecast (`lstm_oni_forecast`) plus the tabular feature set. |
| Horizons | **1, 3, 6 months** — separate artifacts per horizon: `model/enso_ensemble_{1m,3m,6m}/` containing `lstm_horizon_*.pt`, `lightgbm_horizon_*.txt`, feature/target scalers, `metrics_horizon_*.json`, `test_predictions_horizon_*.csv`. |
| Best horizon | `model/model_manifest.json` → `best_validation_horizon_months: 1`. |

**Features actually used** (`dataset/train_features.csv`): ONI anomaly/total,
SOI, DMI, Niño 3.4 SST + zonal SST gradient, regional SST (Karimata, Makassar,
Java, Maluku), per-region MHW counts/intensity, rainfall proxies, seasonal
sin/cos, ENSO coupling index, plus lag (1/2/3/6/12 m) and rolling features.

**Targets:** `target_oni_lead_{1,3,6}m` and `target_phase_lead_{1,3,6}m`.

### Verified metrics (exact, from `metrics_horizon_*.json`)

| Horizon | Validation accuracy | Balanced accuracy | Macro F1 | LSTM ONI RMSE |
| --- | --- | --- | --- | --- |
| **1 bulan** | **0.769** | **0.792** | 0.668 | 1.175 °C |
| 3 bulan | 0.231 | 0.500 | 0.188 | 1.257 °C |
| 6 bulan | 0.000 | 0.000 | 0.000 | 1.258 °C |

- 1-month **test**: accuracy 0.714, balanced accuracy 0.714, macro F1 0.417,
  LSTM RMSE **0.1796 °C** (7 samples).
- 3-month **test**: accuracy 1.000 on 7 samples that are *all Neutral* — this is
  a trivial all-Neutral prediction, **not** evidence of 3-month skill.
- 6-month: validation and test collapse (predicts one dominant class).
- **Rule for the UI:** skill is demonstrated at **1 month only**. 3- and
  6-month leads must be shown as *not yet demonstrated* (honest, muted,
  explicitly labeled), never presented as validated skill.

### Honesty constraints (hard requirements)

1. The trained pipeline targets **ONI**; the dashboard hero currently displays
   **RONI**. Do not claim the RONI outlook is a validated model output unless
   the number is sourced from the metrics files.
2. Landing/dashboard probabilities, MAE benchmark and forecast plume in
   `frontend/src/data/climateData.js` are **reference / simulated** values
   pending backend integration. Tag them ⚠️ "Simulasi" / "Data contoh".
3. Real reference index values already in the dataset (mark ✅):
   RONI **+0,62 °C**, SOI **−7,8**, DMI **+0,12**.
4. Validated 1-month hindcast on 7 test samples: KMRV MAE **0,17 °C** vs
   persistence MAE **0,11 °C**. Persistence is better on this small sample.
   The number may be displayed with that caveat; **never** phrase it as "KMRV
   beats persistence" or "KMRV is more accurate than benchmarks".
5. No daily weather prediction. No deterministic "will be El Niño" claims.
   BMKG remains the official early-warning authority — show that attribution.
6. **Forbidden in any generated UI copy or fake data:** model names other than
   "Causal LSTM + LightGBM ensemble"; any GNN, Transformer, XGBoost, Prophet,
   ARIMA, or "custom neural network" architecture; invented datasets (no
   Copernicus-only, no in-house proprietary data); invented accuracy like
   "95% accurate", "state-of-the-art"; dashboards implying operational
   deployment or BMKG partnership.

---

## 3. Visual system (from `frontend/src/tokens.css`)

- **Theme:** modern SaaS light. Canvas `#F8FAFC` (slate 50), cards pure
  `#FFFFFF`, secondary surfaces `#F1F5F9`, borders `#E2E8F0`.
- **Text:** primary `#0F172A`, secondary `#334155`, muted `#64748B`.
- **Brand:** electric blue `#2563EB` (hover `#1D4ED8`, soft wash `#EFF6FF`).
- **ENSO semantics (colour + label always together, never colour alone):**
  El Niño `#EA580C` (warm/orange), La Niña `#0284C7` (cool/sky), Neutral
  `#64748B` (slate).
- **Functional:** success `#10B981`, warning `#F59E0B`, error `#EF4444`,
  MHW active `#EA580C`.
- **Type:** Inter. Scale: hero 36px, display 30px, section 20px, title 17px,
  body 15px, small 13.5px, micro 12px. Numerals in tabular monospace
  (Geist Mono / SF Mono) for figures.
- **Layout:** 1320px max container, 28px gutters, 20px panel gap, 60px top app
  bar. Cards radius 12px, inputs 8px, pills fully rounded.
- **Elevation:** subtle — `0 1px 3px rgba(0,0,0,.06)` cards, `0 6px 16px` on
  hover. No heavy drop shadows, no gradients except a soft sky wash on the
  landing hero.
- **Motion:** 120–350ms, `cubic-bezier(.16,1,.3,1)`. Respect reduced motion.
- **Data-viz rules:** forecast region drawn with a dashed segment + 80%
  uncertainty band (`rgba(37,99,235,.12)`); measurements solid; always label
  axes with units (°C) and Indonesian decimal commas ("+0,94 °C").

---

## 4. Information architecture (actual app)

```
Landing  (#landing)
└── Dashboard
    ├── Ringkasan            → hero phase + probability, RONI trace, quick stats
    ├── Prakiraan ENSO       → 1/3/6-month lead selector, probability bars,
    │                          forecast plume with uncertainty band
    ├── Laut                 → SST telemetry table/map for 5 domains, MHW events
    └── Dampak Indonesia     → seasonal rainfall-response matrix (heatmap)
```

Top app bar: brand mark ("KMRV"), 4 nav items, region search pill, sync status,
°C/°F toggle, alert bell, avatar. A persistent footer carries data provenance
and the honesty note. Optional secondary pages that exist in the codebase but
are not routed: `KepercayaanModel` (model evaluation), and glossary content.

---

## 5. Master style prompt (append to every screen)

> Design a modern scientific SaaS dashboard for a university climate-intelligence
> project. Light theme, canvas #F8FAFC, white cards with 12px radius and 1px
> #E2E8F0 borders, Inter typography, electric-blue #2563EB accent, orange
> #EA580C for El Niño, sky-blue #0284C7 for La Niña, slate #64748B for Neutral.
> Tabular monospace numerals. Indonesian interface copy. Calm, precise,
> generously spaced, no decorative gradients or stock photos. Every chart has a
> title, unit, and a visible uncertainty indication. Small provenance/legend
> line under each data block. Desktop 1440px, 1320px content width.

---

## 6. Screen prompts for Stitch

### 6.1 Landing page

> A single-screen hero for "KMRV — Proyeksi ENSO Maritim Indonesia". Left 55%:
> a small wave/trace logo mark, eyebrow "Proyeksi ENSO Maritim Indonesia",
> 40px headline "Membaca El Niño dari suhu laut Indonesia", one-sentence
> subhead explaining probabilistic 1/3/6-month ENSO outlooks for Indonesian
> seas, a primary button "Buka Dashboard" and a secondary "Lihat Metode".
> Three trust chips beneath: "Causal LSTM + LightGBM", "Data NOAA OISST v2.1",
> "Validasi 1 bulan: akurasi 0,77". Right 45%: a card showing the current
> reference state — large "El Niño Lemah", RONI "+0,62 °C" with a ✅ marker, a
> small solid sparkline for the last 12 months and a short dashed forecast tail
> with a light-blue uncertainty band. A footer strip: "Data referensi NOAA CPC
> & BOM. Prakiraan bersifat probabilistik. Peringatan resmi: BMKG." Muted note
> "Sebagian angka masih simulasi" with a ⚠️ tag. No photography.

### 6.2 Dashboard shell / app bar

> Full-width 60px top app bar on #F8FAFC: left brand "KMRV" with a small wave
> trace mark; centered inline nav tabs "Overview", "Weather Map", "Station
> Logs", "Rainfall Impact" with the active tab underlined in #2563EB; a rounded
> search input with a magnifier icon and placeholder "Cari domain, stasiun,
> koordinat..."; right side: a subtle sync status "Synced 2 min ago" with a
> refresh icon, a "°C / °F" toggle, a circular alert bell with a small orange
> ping dot, and a 32px circular avatar reading "KM". Thin bottom divider
> #E2E8F0. Content area below has 28px side padding and a 1320px max width.

### 6.3 Ringkasan (Overview)

> Dashboard overview grid. Top row: one large hero card (span 7) titled
> "Status ENSO" showing a big phase label "El Niño Lemah", a 44px RONI figure
> "+0,62 °C", a status caption "November 2026 · rata-rata bergerak 3 bulan", and
> a ✅ "Data referensi NOAA CPC" tag. Beside it (span 5) a "Peluang Fase"
> card with three horizontal probability bars: El Niño 58%, Neutral 34%,
> La Niña 8%, each with a colour dot and a ⚠️ "Simulasi" tag in the card header.
> Second row: a wide "Jejak RONI 24 bulan + prakiraan 6 bulan" line chart —
> solid slate line for history, dashed blue line for forecast, translucent blue
> 80% band, a zero baseline, month labels Nov 24 → Apr 27, y-axis in °C.
> Right of it a compact "Indeks Atmosfer" list: SOI −7,8, DMI +0,12, each with
> ✅ real-data tags. Third row: three small stat cards — "Horizon terbaik:
> 1 bulan", "Akurasi validasi 0,77", "RMSE ONI 0,18 °C" — each with a one-line
> footnote of its artifact source. Footer line: "Angka berlabel ⚠️ belum
> divalidasi model."

### 6.4 Prakiraan ENSO (forecast)

> Forecast detail page. Header: title "Prakiraan ENSO" with a segmented control
> "1 bulan · 3 bulan · 6 bulan" (3 bulan selected). Below, a two-column layout.
> Left: "Peluang Fase" card with three large stacked probability rows and a
> compact legend; under it a "Ketidakpastian" note "+0,94 °C ± 0,35 °C (80%)".
> Right: a forecast plume chart — historical ONI/RONI line, dashed forecast
> line, widening uncertainty cone, target month labelled "Februari 2027",
> y-axis °C. A banner above the chart: "Lead 3 bulan: keterampilan model belum
> terbukti (akurasi validasi 0,23, cenderung memprediksi Neutral)". Amber
> warning styling, small text, dismissible. At the bottom, a compact table
> "Ambang fase ONI": El Niño ≥ +0,5 °C, La Niña ≤ −0,5 °C, Neutral between,
> with the official 5-consecutive-overlapping-season rule. Every panel header
> carries a provenance tag; simulated numbers get ⚠️.

### 6.5 Laut (SST telemetry)

> Marine telemetry page. Header "Telemetri Suhu Laut" with a region filter and
> a date stamp. Main: a five-row data table — domains "Pasifik Niño 3.4",
> "Selat Makassar", "Selat Karimata", "Selatan Jawa", "Maluku–Papua" — columns
> SST (°C), climatology, anomaly (signed, orange for warm / blue for cool),
> MHW status badge, duration, intensity. Niño 3.4 row carries a ✅ "referensi"
> tag, the four Indonesian seas rows carry ⚠️ "Simulasi". A right-side card
> "Kejadian Marine Heatwave" listing active/ended events with category pills
> (Kategori II Moderat, Kategori I Lemah), duration, and a one-line ecosystem
> impact. Include a small map placeholder of the Indonesian archipelago with
> five labelled points/boxes, brand-blue markers; keep it schematic, no
> satellite imagery. Footnote: "Definisi MHW: Hobday et al. (2016)."

### 6.6 Dampak Indonesia (rainfall matrix)

> Impact page. Title "Dampak Musiman di Indonesia" with a note "Respons curah
> hujan saat El Niño aktif, deviasi dari klimatologi 1991–2020". Centerpiece:
> a heatmap matrix — rows are regions (Sumatera selatan, Jawa–Bali–Nusa
> Tenggara, Kalimantan selatan–tengah, Sulawesi selatan–tenggara,
> Maluku–Papua), columns DJF, MAM, JJA, SON — each cell a percentage with a
> diverging warm-to-cool scale (dry = orange, wet = blue) and the number
> printed inside. Hover/selected state shows a detail card with the region's
> primary risk sentence. Add a legend strip for the diverging scale and a
> persistent ⚠️ "Simulasi — belum keluaran model" tag. Right column: three
> "Rekomendasi" cards (water, agriculture, fire risk) written as cautious
> advisories, not deterministic forecasts. Footer attribution to BMKG for
> official warnings.

### 6.7 Metode / Kepercayaan Model (optional, for the examiner)

> Methodology page, documentation-first, mostly typography. Two-column reading
> layout. Section 1 "Arsitektur": a small horizontal pipeline diagram —
> 12-month feature window → Causal LSTM (hidden 32) → ONI forecast →
> LightGBM (3 kelas) → probabilitas fase. Section 2 "Data & fitur": source
> list with ✅ tags (NOAA OISST v2.1, NOAA CPC RONI/ONI, BOM SOI, DMI, CHIRPS/
> ERA5) and the Jan 2015 – Dec 2025 window. Section 3 "Evaluasi": a clean
> metrics table for horizons 1/3/6 months with accuracy, balanced accuracy,
> macro-F1, RMSE — 1 bulan row highlighted as the only demonstrated horizon,
> 3 and 6 bulan rows muted with "belum terbukti". Section 4 "Keterbatasan":
> honest bullets (small test set, ONI vs RONI mismatch, persistence benchmark
> competitive, spring predictability barrier, backend not yet implemented).
> Section 5 "Reproduksi": one-line command `python main.py --horizons 1 3 6`.
> No inflated claims anywhere on this page.

---

## 7. Negative prompt (add to Stitch where supported)

> No invented model architectures, no "AI-powered" marketing language, no
> accuracy percentages other than those listed, no fake citations, no
> testimonials, no partner logos (BMKG is an authority reference, not a
> partner), no dark-mode-first design, no 3D globes, no stock photography,
> no animated weather icons, no red/green only status encoding, no gradients
> on charts.
