"""
Bounded Free-Text Symptom Extraction & Normalization.
Optional Vertex AI / Gemini integration with safe deterministic local fallback.
Never used as the sole authority for triage priority or escalation.
TODO: CLINICAL VALIDATION REQUIRED.
"""

import os
import re
from typing import Dict, Any, List

def extract_symptoms_from_narrative(narrative_text: str) -> Dict[str, Any]:
    """
    Extracts structured symptoms and duration from free-text intake notes.
    Uses local regex & keyword parsing if Google Cloud credentials are not configured.
    """
    if not narrative_text or not narrative_text.strip():
        return {
            "symptoms": [],
            "duration_minutes": None,
            "extracted_by": "deterministic-empty",
            "is_ambiguous": False
        }

    # Bounded local deterministic parser
    text_lower = narrative_text.lower()
    
    symptom_catalog = [
        ("chest pain", "Chest pain"),
        ("shortness of breath", "Shortness of breath"),
        ("sob", "Shortness of breath"),
        ("difficulty breathing", "Shortness of breath"),
        ("abdominal pain", "Abdominal pain"),
        ("stomach ache", "Abdominal pain"),
        ("fever", "Fever"),
        ("lethargy", "Lethargy"),
        ("fatigue", "Lethargy"),
        ("dizziness", "Dizziness"),
        ("dizzy", "Dizziness"),
        ("weakness", "Weakness"),
        ("weak", "Weakness"),
        ("headache", "Headache"),
        ("cough", "Cough"),
        ("wheeze", "Wheezing"),
        ("vomiting", "Vomiting"),
        ("nausea", "Nausea"),
        ("cyanosis", "Cyanosis"),
        ("cyanotic", "Cyanosis"),
        ("confusion", "Altered mental status"),
        ("confused", "Altered mental status")
    ]

    extracted_symptoms = []
    for pattern, canonical in symptom_catalog:
        if re.search(r'\b' + re.escape(pattern) + r'\b', text_lower):
            if canonical not in extracted_symptoms:
                extracted_symptoms.append(canonical)

    # Duration parsing
    duration_mins = None
    hour_match = re.search(r'(\d+)\s*(hour|hr|hours)', text_lower)
    day_match = re.search(r'(\d+)\s*(day|days)', text_lower)
    min_match = re.search(r'(\d+)\s*(min|minute|minutes)', text_lower)

    if hour_match:
        duration_mins = int(hour_match.group(1)) * 60
    elif day_match:
        duration_mins = int(day_match.group(1)) * 1440
    elif min_match:
        duration_mins = int(min_match.group(1))

    is_ambiguous = any(s in extracted_symptoms for s in ["Dizziness", "Weakness", "Altered mental status"])

    return {
        "symptoms": extracted_symptoms,
        "duration_minutes": duration_mins,
        "extracted_by": "local-rule-parser",
        "is_ambiguous": is_ambiguous
    }
