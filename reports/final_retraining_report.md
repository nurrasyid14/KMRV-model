# Final ENSO forecasting model and forecast

- Forecast origin: **2025-06**.
- Requested period: **18 months**.
- Model-supported direct leads: **1, 3, 6**.
- Unsupported requested leads: **15**; these are not interpolated or recursively forecast.
- Model status: **experimental forecasting candidate; not approved for production**.
- Phase probabilities are classifier outputs and are **not calibrated probabilities**.

## Retraining and evaluation separation

The separate `model/final_retrained/` artifacts use all target observations whose target month is no later than the final historical data month. This includes rows previously used in training, validation, and test. Historical backtesting outputs are not changed. No final retraining score is reported as an independent test result, and no test metric is used to choose the frozen model family or imbalance strategy.

Candidates are frozen from the existing validation-only selection record: XGBoost/balanced at 1 and 6 months, and LightGBM/unweighted at 3 months. They remain provisional because the historical record has one validation and one test period, and validation also informed tree early stopping.

## Leakage controls

- Target rows are eligible only when `origin + horizon <= forecast origin`; the 12-month input window ends at its origin.
- LSTM feature and target scalers are fitted only on eligible historical features/targets for each lead. No imputer or feature selection is used.
- Classifier fitting uses chronological expanding-window out-of-fold LSTM forecasts; no in-sample LSTM predictions are used.
- Future climate features and future ONI are not generated or read for inference. The direct forecast uses the latest historical feature window.
- Notebook engineering constructs lag features with positive shifts and rolling features from lag-1 values; no target columns enter the feature schema.
- Continuous ONI and phase are separate model outputs; the classifier phase can disagree with the LSTM's ONI threshold.

## Feature availability and forecast limitations

The dataset does not record source-specific publication/availability timestamps. Contemporary ONI, SST, MHW, SOI/DMI, and rainfall values are used at the forecast origin, so the forecasts are conditional on those monthly values having been finalized and available at issuance. This has not been independently verified; the audit records it as an unresolved operational limitation. Accordingly, the audit is not marked fully passed and the artifacts are not production-approved.

Current models support direct leads 1, 3, and 6 only. For an 18-month request, only July 2025, September 2025, and December 2025 are predicted for a June 2025 origin. The other 15 months are explicitly unsupported. Full monthly coverage requires separately trained and temporally evaluated direct models for each lead, or a separately validated recursive system that forecasts every required input variable.

## Forecast rows

| Lead (months) | Target month | Predicted ONI | Predicted phase |
| ---: | --- | ---: | --- |
| 1 | 2025-07 | -0.2359 | Neutral |
| 3 | 2025-09 | -0.6351 | Neutral |
| 6 | 2025-12 | -0.0744 | El Nino |

## Visualizations

- `reports\final_retrained\historical_and_forecast_oni.png`
- `reports\final_retrained\historical_and_forecast_phase.png`
- `reports\final_retrained\forecast_phase_probabilities.png`
- `reports\final_retrained\forecast_horizon_1m.png`
- `reports\final_retrained\forecast_horizon_3m.png`
- `reports\final_retrained\forecast_horizon_6m.png`

The exact machine-readable audit is in `reports/final_retraining_leakage_audit.json`; supported forecast rows are in `reports/final_retrained/forecast.csv` and `forecast.json`.

## Run

```powershell
python main.py --final-retrain --forecast-months 18
```
