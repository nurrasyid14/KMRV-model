"""XGBoost phase classifier shared by the ENSO ensemble."""

from __future__ import annotations

import pandas as pd
import xgboost as xgb


def create_phase_classifier(
    random_state: int = 42,
    iterations: int = 300,
    early_stopping_rounds: int | None = 50,
) -> xgb.XGBClassifier:
    return xgb.XGBClassifier(
        objective="multi:softmax",
        num_class=3,
        n_estimators=iterations,
        learning_rate=0.03,
        max_depth=3,
        min_child_weight=1,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_lambda=1.0,
        random_state=random_state,
        eval_metric="mlogloss",
        early_stopping_rounds=early_stopping_rounds,
        tree_method="hist",
        n_jobs=-1,
        verbosity=0,
    )


def train_phase_classifier(
    train_features: pd.DataFrame,
    train_labels,
    validation_features: pd.DataFrame,
    validation_labels,
    random_state: int = 42,
) -> xgb.XGBClassifier:
    model = create_phase_classifier(random_state=random_state)
    model.fit(
        train_features,
        train_labels,
        eval_set=[(validation_features, validation_labels)],
        verbose=False,
    )
    return model