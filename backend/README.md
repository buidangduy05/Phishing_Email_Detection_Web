# Mailguard backend

FastAPI backend for analyzing `.eml` messages. The frontend posts the message
as multipart form data in the `file` field to `POST /api/analyze`.

## Run locally

Use Python 3.12 (the recommended runtime for the Doc2Vec dependency).

```sh
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API allows `http://localhost:5173` by default. Set `CORS_ORIGINS` to a
comma-separated list of trusted frontend origins to change this.

## Model artifacts

Place `doc2vec.model`, `feature_scaler.pkl`, and `selected_model.pkl` in
`backend/artifacts/`. The model input combines the Doc2Vec message embedding
with the 40 hand-crafted features in the stable order in
`app/services/feature_extractor.py`. The scaler may be trained on either the
40 hand-crafted values (which are scaled before concatenating the embedding)
or the complete combined vector. The classifier must return binary classes
(`0`/`1`, safe/phishing, or equivalent labels).

If all artifacts are absent, the API explicitly identifies its preliminary
rule-based fallback in the response. If only some artifacts are present or
they are incompatible with the expected input, the endpoint returns HTTP 503
instead of silently substituting a different classifier.

`POST /api/analyze` returns `isPhishing`, `summary`, `features`, and `model`.
Uploads are limited to 20 MiB. `GET /health` is available for health checks.
