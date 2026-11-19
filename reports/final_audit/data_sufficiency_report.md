# Data sufficiency report

## Effective sample sizes

The feature master contains **114** rows, **67** input features, and a 12-month input window. The classifier receives those features plus one predicted ONI feature (**68** inputs). It is trained only on retained causal LSTM OOF rows: across horizons/folds, the OOF training set ranges from **24** to **35** rows. The smallest OOF set has fewer rows than features, so flexible tree models can overfit severely. **12** validation candidate rows have full class coverage.

| Horizon | La Niña | Neutral | El Niño | Total labeled rows |
| --- | ---: | ---: | ---: | ---: |
| 1 | 31 | 52 | 31 | 114 |
| 3 | 31 | 54 | 29 | 114 |
| 6 | 34 | 53 | 27 | 114 |

Purging and the sliding window reduce usable validation rows to 23, 21, and 18 for horizons 1, 3, and 6; the terminal test period has 18 origins. The actual per-fold train/OOF/validation/test counts and class distributions are in `class_coverage_report.csv`:

| horizon | fold1_train_n | fold1_classifier_train_oof_n | fold1_validation_n | fold1_validation_coverage | fold1_test_n | fold1_test_coverage |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 60 | 35 | 23 | 3/3 | 18 | 2/3 |
| 3 | 58 | 27 | 21 | 3/3 | 18 | 2/3 |
| 6 | 55 | 24 | 18 | 3/3 | 18 | 2/3 |

## Interpretation and recommendations

- **114 samples are not sufficient for a reliable three-class, multi-horizon model-selection claim.** The configured run has only one 18-month test period and one validation period; it cannot measure between-period stability.
- Extend the historical record to multiple decades if a homogeneous source with consistent feature definitions is available. Do not synthesize observations or rebalance validation/test.
- **67 features are too many relative to the OOF classifier sample sizes in this experiment.** Reduce to a small, domain-justified candidate set and compare against persistence/climatology baselines.
- No feature selection is applied in this audit. If introduced, fit the selector independently inside each outer training fold (and inside the OOF training procedure where applicable); never select using the full dataset or test labels.
- Keep all horizons separate. The 6-month horizon has the fewest validation origins and particularly small OOF samples.
- A 24-month validation interval offers more support at horizon 6 than an 18-month interval while retaining 72 training months. `validation_window_sweep.csv` compares it with 18-, 30-, and 36-month alternatives. Outer validation still controls tree-classifier early stopping and is not an independent model-selection estimate; LSTM epoch selection uses an internal segment of the training period.
- The previous 60/18/18 layout generated two folds, but its first validation omitted El Niño and its second validation reused prior test origins. Generating more than two folds here would require shorter validation/test intervals; a 12-month validation leaves only six horizon-6 origins after purge, so it was rejected.
- Current data cannot support several independent validation and test periods with adequate class coverage. Extend the record before interpreting fold variability or claiming stable model selection.

This report assesses data sufficiency only; it does not alter features, retrain models, or change saved model artifacts.
