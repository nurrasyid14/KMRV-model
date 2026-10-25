"""Planned learning workflow:

1. Load the SST and anomaly variables from the prepared Zarr stores and align
   them with the daily ENSO and IOD indices.
2. Split the records chronologically into training, validation, and test sets
   to avoid leaking future observations into model training.
3. Fit preprocessing statistics on the training split, apply the same
   transformation to the other splits, and create sliding time-series windows.
4. Train an LSTM on the historical SST/anomaly windows, then use its learned
   temporal features together with ENSO/IOD features in a LightGBM model to
   estimate SST anomaly, marine-heatwave category, and duration.
5. Evaluate the models on the held-out dates, save model artifacts and
   evaluation metrics, and pass validated predictions to the inference and
   persistence stages.

This module documents the intended workflow only; training and inference have
not been implemented yet.
"""
