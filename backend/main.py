import logging
import os

import requests
from fastapi import FastAPI, HTTPException, Query

logger = logging.getLogger(__name__)
MODEL_SERVICE_URL = os.getenv("MODEL_SERVICE_URL", "http://localhost:8001").rstrip("/")
MODEL_TIMEOUT_SECONDS = 30
AVAILABLE_HORIZONS = (1, 3, 6)

app = FastAPI(title="ENSO Forecast API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/forecast/latest")
def latest_forecast(
    horizon: int = Query(default=1),
) -> dict[str, object]:
    if horizon not in AVAILABLE_HORIZONS:
        raise HTTPException(
            status_code=422,
            detail=f"horizon must be one of {AVAILABLE_HORIZONS}",
        )
    try:
        response = requests.get(
            f"{MODEL_SERVICE_URL}/api/v1/forecast/latest",
            params={"horizon": horizon},
            timeout=MODEL_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.Timeout as exc:
        logger.exception("Timed out requesting forecast from model service")
        raise HTTPException(
            status_code=504,
            detail="Model inference timed out",
        ) from exc
    except requests.RequestException as exc:
        logger.exception("Model service request failed")
        raise HTTPException(
            status_code=502,
            detail="Model inference service is unavailable",
        ) from exc

    return response.json()
