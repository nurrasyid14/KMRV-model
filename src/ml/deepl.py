"""PyTorch sequence models for climate and impact forecasting."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

try:
    import torch
    from torch import nn
except ImportError:  # pragma: no cover - handled explicitly by the orchestrator
    torch = None
    nn = None


@dataclass
class SequenceWindow:
    """Monthly samples arranged as [sample, window, feature]."""

    features: np.ndarray
    targets: np.ndarray


def make_sequence_windows(
    features: np.ndarray,
    targets: np.ndarray,
    window_size: int,
) -> SequenceWindow:
    """Create aligned sliding windows without crossing chronological samples."""
    features = np.asarray(features, dtype=np.float32)
    targets = np.asarray(targets, dtype=np.float32)
    if window_size < 1:
        raise ValueError("window_size must be at least 1")
    if features.ndim != 2 or targets.ndim == 0:
        raise ValueError("features and targets must be two-dimensional or one-dimensional")
    if len(features) != len(targets):
        raise ValueError("features and targets must have the same length")
    if len(features) <= window_size:
        raise ValueError("window_size leaves no training sample")

    windowed_features = np.stack(
        [features[index:index + window_size] for index in range(len(features) - window_size)]
    )
    windowed_targets = targets[window_size:]
    return SequenceWindow(windowed_features, windowed_targets)


class ClimateLSTM(nn.Module if nn is not None else object):
    """Compact LSTM for monthly multivariate forecasts."""

    def __init__(
        self,
        input_size: int,
        hidden_size: int = 64,
        output_size: int = 1,
        num_layers: int = 1,
    ) -> None:
        if torch is None:
            raise RuntimeError("torch must be installed to create ClimateLSTM")
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
        )
        self.head = nn.Linear(hidden_size, output_size)

    def forward(self, features):
        encoded, _ = self.lstm(features)
        return self.head(encoded[:, -1])
