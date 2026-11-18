# Temporal integrity report

## Dataset and ordering

- Dataset: `dataset\features_master_unscaled.csv`
- Rows and date span: **114**, 2016-01-01 to 2025-06-01.
- Input features: **67** numeric columns.
- Raw CSV timestamps already ordered: **True**; unique and contiguous month-start timestamps are enforced by the loader.
- Missing/non-finite input feature values after loading: **0 / 0**. The backtest rejects missing/non-finite values; it does not fit an imputer.

## Target alignment

`load_feature_data` orders rows by time and validates targets against `oni_anom.shift(-h)`. The independent checks below compare every origin for which the future ONI is present within this 114-row table:

| horizon_months | verified_origins | mismatches | status |
| --- | --- | --- | --- |
| 1 | 113 | 0 | pass |
| 3 | 111 | 0 | pass |
| 6 | 108 | 0 | pass |

The feature-engineering notebook constructs each target using `oni_anom.shift(-lead)` and filters rows using the six-month target's non-null mask. Its recorded output reports 132 monthly source rows before filtering, which is consistent with target observations beyond the final feature timestamp. Source-shift/filter evidence present: **True**. The retained target ends up to December 2025 although predictor rows end in June 2025. The underlying Zarr ONI source was not reloaded during this audit, so the terminal values' provenance is supported by notebook code/output, not an independent raw-source recomputation.

## Purge and overlapping windows

For each horizon, train origins satisfy `origin + horizon < validation_start`, and validation origins satisfy `origin + horizon < test_start`:

| fold | horizon | train_target_before_validation | validation_target_before_test |
| --- | --- | --- | --- |
| 1 | 1 | True | True |
| 1 | 3 | True | True |
| 1 | 6 | True | True |

Purge checks: **PASS**. A 12-month input window may cross a split boundary to use earlier observed feature history; it does not expose a future target. The window ends at its forecast origin. This historical context overlap is valid for rolling forecasts.

Fold independence:

_No rows available._

No later validation fold reuses an earlier test period in the configured one-fold evaluation.

## Preprocessing and feature selection

- Feature scaling is fit in `_fit_lstm` using feature rows no later than the final training origin; the ONI target scaler is fit only on training target origins. Validation/test values are transformed, never fit.
- No imputer is fitted in the backtest. The loader fails on null/non-finite features.
- The active backtest uses all 67 input features; it does not perform feature selection.
- The notebook contains a full-dataset top-correlation calculation for a visualization. It is not applied to the backtest feature list. Using those target-correlated features as a selected model input would leak validation/test information; any future selection must be performed inside each training fold only.
- Current-month ONI/SST/rain features are available to the model at the row's origin. Operational use requires a declared data-availability/issuance cutoff; this audit cannot establish that all contemporaneous monthly aggregates would be available on an actual forecast date.

Overall temporal/target checks: **PASS**.
