"""LightGBM phase classifier shared by ENSO backtesting."""

from __future__ import annotations

import lightgbm as lgb


def create_phase_classifier(
    random_state: int = 42,
    iterations: int = 300,
    class_weight: dict[int, float] | None = None,
) -> lgb.LGBMClassifier:
    return lgb.LGBMClassifier(
        objective="multiclass",
        num_class=3,
        n_estimators=iterations,
        learning_rate=0.03,
        num_leaves=7,
        max_depth=3,
        min_child_samples=5,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_lambda=1.0,
        random_state=random_state,
        class_weight=class_weight,
        verbosity=-1,
    )


def train_phase_classifier(
    train_features,
    train_labels,
    validation_features,
    validation_labels,
    random_state: int = 42,
    class_weight: dict[int, float] | None = None,
) -> lgb.LGBMClassifier:
    model = create_phase_classifier(
        random_state=random_state,
        class_weight=class_weight,
    )
    model.fit(
        train_features,
        train_labels,
        eval_set=[(validation_features, validation_labels)],
        callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(0)],
    )
    return model
