from pathlib import Path
from typing import Any, Dict

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, ValidationError

from url_features import FEATURE_COLUMNS, extract_features


MODEL_PATH = Path("model/phishing_model.joblib")


class UrlRequest(BaseModel):
    url: HttpUrl | str


class PredictionResponse(BaseModel):
    url: str
    is_phishing: bool
    probability_phishing: float
    model_version: str = "v1"


def load_model() -> Dict[str, Any]:
    if not MODEL_PATH.exists():
        raise RuntimeError(
            f"Model file not found at {MODEL_PATH}. Train the model first using train_model.py."
        )
    bundle = joblib.load(MODEL_PATH)
    if "pipeline" not in bundle:
        raise RuntimeError("Invalid model bundle: expected 'pipeline' key.")
    return bundle


bundle = load_model()
pipeline = bundle["pipeline"]
decision_threshold: float = float(bundle.get("decision_threshold", 0.5))

app = FastAPI(title="URL Phishing Detection API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(request: UrlRequest) -> PredictionResponse:
    # Accept both well-formed URLs and raw strings
    try:
        url_str = str(request.url)
    except ValidationError:
        url_str = str(request.url)

    features = extract_features(url_str)
    X = [[features[col] for col in FEATURE_COLUMNS]]

    try:
        proba_phishing = float(pipeline.predict_proba(X)[0][1])
        label = bool(proba_phishing >= decision_threshold)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return PredictionResponse(
        url=url_str,
        is_phishing=label,
        probability_phishing=proba_phishing,
    )


