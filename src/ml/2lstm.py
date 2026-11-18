"""PyTorch LSTM model components for ENSO forecasting."""

from __future__ import annotations

import copy

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


class CausalLSTM(nn.Module):
    def __init__(self, feature_count: int, hidden_size: int, dropout: float) -> None:
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=feature_count,
            hidden_size=hidden_size,
            num_layers=1,
            batch_first=True,
        )
        self.dropout = nn.Dropout(dropout)
        self.output = nn.Linear(hidden_size, 1)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        _, (hidden, _) = self.lstm(inputs)
        return self.output(self.dropout(hidden[-1])).squeeze(-1)


def train_causal_lstm(
    train_windows: tuple[torch.Tensor, torch.Tensor] | tuple[object, object],
    validation_windows: tuple[torch.Tensor, torch.Tensor] | tuple[object, object],
    feature_count: int,
    hidden_size: int,
    epochs: int,
    batch_size: int,
    learning_rate: float,
) -> tuple[CausalLSTM, list[dict[str, float]]]:
    train_x, train_y = train_windows
    val_x, val_y = validation_windows
    model = CausalLSTM(feature_count, hidden_size, dropout=0.1)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loss_function = nn.MSELoss()
    loader = DataLoader(
        TensorDataset(torch.from_numpy(train_x), torch.from_numpy(train_y)),
        batch_size=batch_size,
        shuffle=True,
    )
    validation_x = torch.from_numpy(val_x)
    validation_y = torch.from_numpy(val_y)

    best_state: dict[str, torch.Tensor] | None = None
    best_mse = float("inf")
    patience = 0
    history: list[dict[str, float]] = []
    for epoch in range(epochs):
        model.train()
        for batch_x, batch_y in loader:
            optimizer.zero_grad()
            loss = loss_function(model(batch_x), batch_y)
            loss.backward()
            optimizer.step()

        model.eval()
        with torch.no_grad():
            validation_mse = loss_function(
                model(validation_x),
                validation_y,
            ).item()
        history.append({"epoch": float(epoch + 1), "validation_mse": validation_mse})
        if validation_mse < best_mse - 1e-5:
            best_mse = validation_mse
            best_state = copy.deepcopy(model.state_dict())
            patience = 0
        else:
            patience += 1
        if patience >= 30:
            break

    if best_state is not None:
        model.load_state_dict(best_state)
    return model, history