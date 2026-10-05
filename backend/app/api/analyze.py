from fastapi import APIRouter, File, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from app.core.config import MAX_UPLOAD_SIZE
from app.models.schemas import AnalysisResponse, EmailFeature
from app.services.email_parser import parse_email
from app.services.explanation import explain_risks
from app.services.feature_extractor import extract_features
from app.services.inference import predict_email
from app.services.preprocessing import prepare_email


router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_email(file: UploadFile = File(...)) -> AnalysisResponse:
    if not file.filename or not file.filename.lower().endswith(".eml"):
        raise HTTPException(status_code=400, detail="Upload an .eml email file.")
    raw_email = await file.read(MAX_UPLOAD_SIZE + 1)
    if len(raw_email) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="Email file exceeds the 20 MB size limit.")
    if not raw_email:
        raise HTTPException(status_code=400, detail="The uploaded email file is empty.")
    try:
        email = parse_email(raw_email)
    except (ValueError, UnicodeError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    normalized = prepare_email(email)
    features = extract_features(email)
    try:
        result = await run_in_threadpool(
            predict_email,
            normalized["subject"],
            normalized["body"],
            features,
        )
    except (RuntimeError, OSError, ValueError) as error:
        raise HTTPException(status_code=503, detail=f"Email analysis is unavailable: {error}") from error

    indicators = explain_risks(features) if result.is_phishing else []
    if result.model == "heuristic-fallback":
        summary = (
            "Preliminary rule-based analysis flagged this message. "
            "No trained model artifacts are configured."
            if result.is_phishing
            else "No high-risk indicators were found by the preliminary rule-based analysis. "
            "No trained model artifacts are configured."
        )
    else:
        summary = (
            "The trained model identified phishing indicators in this message."
            if result.is_phishing
            else "The trained model did not identify this message as phishing."
        )
    return AnalysisResponse(
        isPhishing=result.is_phishing,
        summary=summary,
        features=[EmailFeature(**indicator) for indicator in indicators],
        model=result.model,
    )
