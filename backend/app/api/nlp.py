"""
Bounded NLP & Symptom Extraction API.
Provides bounded structured symptom extraction from free-text intake notes.
Does NOT assign triage priority or bypass downstream safety/ML engines.
TODO: CLINICAL VALIDATION REQUIRED.
"""

from fastapi import APIRouter, HTTPException
from app.schemas.schemas import SymptomExtractionRequest, SymptomExtractionResponse
from app.ml.symptom_extractor import extract_symptoms_from_narrative

router = APIRouter(prefix="/nlp", tags=["NLP & Symptom Extraction"])

@router.post("/extract-symptoms", response_model=SymptomExtractionResponse)
def extract_symptoms_endpoint(payload: SymptomExtractionRequest):
    """
    Extracts structured symptoms, duration, and ambiguity flags from free-text presentation.
    Never returns a triage priority. Output is intended as a suggestion for clinician review.
    """
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Presentation narrative cannot be empty.")

    if len(text) > 1000:
        raise HTTPException(status_code=400, detail="Presentation narrative exceeds maximum length (1000 chars).")

    result = extract_symptoms_from_narrative(text)
    return SymptomExtractionResponse(
        symptoms=result["symptoms"],
        duration_minutes=result.get("duration_minutes"),
        extracted_by=result.get("extracted_by", "local-rule-parser"),
        is_ambiguous=result.get("is_ambiguous", False)
    )
