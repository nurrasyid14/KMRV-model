FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1 \
    MODEL_ARTIFACTS_DIR=/app/models/final_retrained \
    FEATURES_FILE=/app/dataset/features_master_unscaled.csv

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY model/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu \
        --no-deps "torch==2.5.1+cpu" \
    && pip install --no-cache-dir -r /app/requirements.txt

RUN mkdir -p /app/src/ml /app/model
COPY model/service.py /app/model/service.py
COPY src/__init__.py /app/src/__init__.py
COPY src/ml/2lstm.py /app/src/ml/2lstm.py

EXPOSE 8001

CMD ["uvicorn", "model.service:app", "--host", "0.0.0.0", "--port", "8001"]
