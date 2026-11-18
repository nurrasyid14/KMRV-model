# Final recommendation

## Decision

**Do not declare a final production model from this experiment.** The configured validation period covers all three classes at every horizon, so validation-only candidate ranking is permitted. The configured run has only one validation period and one test period; outer validation is also used for tree-classifier early stopping, so its ranks remain provisional.

Validation-only diagnostic rank leaders are:

| fold | horizon_months | model | imbalance_strategy | macro_f1_validation | balanced_accuracy_validation |
| --- | --- | --- | --- | --- | --- |
| 1 | 1 | XGBoost | balanced | 0.7336182336182336 | 0.7301587301587302 |
| 1 | 3 | LightGBM | unweighted | 0.4848484848484848 | 0.4571428571428571 |
| 1 | 6 | XGBoost | balanced | 0.3063973063973064 | 0.4047619047619048 |

These ranks use macro-F1, balanced accuracy, per-class precision/recall, and class coverage, with ONI RMSE as a later tie-breaker. Test metrics are descriptive only and were not used to rank candidates. The test period misses classes at some horizons, so its metrics cannot establish recognition of all three phases.

The selected 24-month validation duration is a compromise: it retains 72 training months and yields 23, 21, and 18 usable validation origins for horizons 1, 3, and 6. The 6-month horizon has only four Neutral validation examples, so selection is still uncertain.

## Audit conclusions

1. Raw timestamps are ordered and contiguous; target shifts, target-time purge, training-only scaling, causal lag/rolling construction, and OOF forecast boundaries pass the checks documented in `temporal_integrity_report.md` and `leakage_audit.md`.
2. The single terminal fold avoids cross-fold test/validation reuse, but does not provide independent estimates of temporal stability.
3. The classifier is trained on few OOF rows relative to 68 input dimensions. This is a dominant data-sufficiency concern even after increasing the initial training interval.
4. No model is promoted as a final production choice; rankings and selected checkpoints remain provisional pending independent historical evaluation.

## Next steps

1. Extend the historical record with consistent, timestamped predictors and target definitions; do not generate synthetic test examples.
2. Define forecast issuance time and lag any monthly predictor that would not be available then.
3. Extend the historical record and run nested rolling-origin evaluation with multiple three-class validation and test periods.
4. Establish persistence and climatology baselines, then consider fold-local domain feature selection and regularization.
5. Promote a final model only after class coverage and selection stability are supported by multiple independent validation periods.
