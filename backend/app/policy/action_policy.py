"""
Decision Fusion & Action Policy Engine.
Combines:
1. Deterministic Safety Gate (AcuityGuard)
2. Calibrated ML Risk Estimator (AcuityExplain)
3. Multi-Factor Uncertainty Engine
4. Conservative Action Policy (Preventing Under-Triage)
TODO: CLINICAL VALIDATION REQUIRED.
"""

from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.models.entities import Patient, Observation
from app.policy.population import resolve_population_profile
from app.policy.completeness import calculate_data_completeness
from app.policy.safety_gate import evaluate_safety_gate
from app.ml.risk_model import risk_engine
from app.ml.uncertainty import compute_uncertainty_breakdown, UncertaintyBreakdown

class TriageDecisionResult:
    def __init__(
        self,
        risk_score: float,
        confidence_score: float,
        data_completeness: float,
        priority: str,
        action: str,
        safety_flags: List[str],
        key_signals: List[str],
        missing_information: List[str],
        explanation: str,
        population_profile: str,
        uncertainty_details: Dict[str, Any],
        model_details: Dict[str, Any],
        model_status: str = "CALIBRATED_ML",
        model_available: bool = True,
        model_source: str = "calibrated_model",
        model_version: str = "calibrated-lr-v1.0.0-synthetic"
    ):
        self.risk_score = risk_score
        self.confidence_score = confidence_score
        self.data_completeness = data_completeness
        self.priority = priority
        self.action = action
        self.safety_flags = safety_flags
        self.key_signals = key_signals
        self.missing_information = missing_information
        self.explanation = explanation
        self.population_profile = population_profile
        self.uncertainty_details = uncertainty_details
        self.model_details = model_details
        self.model_status = model_status
        self.model_available = model_available
        self.model_source = model_source
        self.model_version = model_version

def _map_risk_to_priority(risk_score: float) -> str:
    """Maps continuous risk score 0..100 to illustrative priority band."""
    if risk_score >= 75.0:
        return "IMMEDIATE"
    elif risk_score >= 50.0:
        return "HIGH"
    elif risk_score >= 25.0:
        return "MODERATE"
    else:
        return "LOW"

def evaluate_patient_triage(patient: Patient, latest_obs: Optional[Observation]) -> TriageDecisionResult:
    """
    Main Triage Decision Pipeline:
    1. Resolve population profile (pediatric/adult/geriatric)
    2. Compute workflow data completeness
    3. Run deterministic safety gate & conflict detection
    4. Run calibrated ML risk prediction
    5. Compute multi-factor uncertainty breakdown
    6. Apply conservative decision fusion (Safety Gate + Action Policy)
    """
    # 1. Demographic Profile Resolution
    profile = resolve_population_profile(patient.age_years, patient.population_profile)
    patient.population_profile = profile

    # 2. Data Completeness & Missing Fields
    completeness, missing_info = calculate_data_completeness(patient, latest_obs)

    # 3. Deterministic Safety Gate & Conflict Evaluation
    safety_flags, has_conflict, conflict_reasons, gate_signals = evaluate_safety_gate(patient, latest_obs)

    # 4. Calibrated ML Model Inference
    ml_output = risk_engine.predict_risk(patient, latest_obs)
    risk_score = ml_output["risk_score"]
    calibrated_prob = ml_output["calibrated_probability"]
    top_features = ml_output.get("top_features", [])
    model_status = ml_output.get("model_status", "CALIBRATED_ML")
    model_available = ml_output.get("model_available", True)
    model_source = ml_output.get("model_source", "calibrated_model")
    model_version = ml_output.get("model_version", "calibrated-lr-v1.0.0-synthetic")
    source_label = "calibrated ML model" if model_available else "deterministic fallback policy"

    # 5. Multi-Factor Uncertainty Engine
    uncertainty: UncertaintyBreakdown = compute_uncertainty_breakdown(
        patient=patient,
        latest_obs=latest_obs,
        calibrated_prob=calibrated_prob,
        completeness=completeness,
        has_conflict=has_conflict
    )
    confidence = uncertainty.workflow_confidence

    # 6. Base Priority from Risk Score
    base_priority = _map_risk_to_priority(risk_score)
    final_priority = base_priority
    action = "RECOMMEND"
    explanation_parts = []

    # Merge key signals for explainability
    all_signals = list(set(
        gate_signals +
        [f"{f['feature']} (Impact: +{f['impact_weight']})" for f in top_features]
    ))

    # --- DECISION FUSION & CONSERVATIVE ESCALATION RULES ---

    # Rule 1: Conflicting clinical observations -> ABSTAIN & Prompt Clinician Review
    if has_conflict:
        action = "ABSTAIN"
        final_priority = "REVIEW"
        safety_flags.extend(conflict_reasons)
        explanation_parts.append(
            "System abstained from automated scoring: Physiological measurements contradict observed clinical presentation. Immediate clinician verification required."
        )

    # Rule 2: Critical safety flags present -> Safety Gate Overrides ML -> Force IMMEDIATE/HIGH
    elif len(safety_flags) > 0:
        action = "ESCALATE"
        if any("Critical" in f or "Shock" in f or "Crisis" in f for f in safety_flags):
            final_priority = "IMMEDIATE" if risk_score >= 50.0 else "HIGH"
        else:
            final_priority = "HIGH" if base_priority in ["LOW", "MODERATE"] else base_priority
        explanation_parts.append(
            f"Safety override triggered: Critical physiological threshold flags active ({len(safety_flags)} flags). Recommended for immediate clinical escalation."
        )

    # Rule 3: High Uncertainty / Low Confidence -> Bias toward ESCALATE (Never downgrade!)
    elif confidence < settings.MIN_CONFIDENCE_THRESHOLD:
        action = "ESCALATE"
        if base_priority in ["LOW", "MODERATE"]:
            final_priority = "REVIEW"
        explanation_parts.append(
            f"Uncertainty flag: Workflow confidence is {confidence}% (statistical decision margin {uncertainty.model_certainty}%, data completeness {uncertainty.data_reliability}%). Escalated for clinician review to prevent under-triage."
        )

    # Rule 4: Incomplete Data on Concerning / Moderate+ Presentation -> ESCALATE (Never guess LOW)
    elif completeness < settings.MIN_COMPLETENESS_THRESHOLD and (
        base_priority in ["MODERATE", "HIGH", "IMMEDIATE"]
        or (patient.pain_score is not None and patient.pain_score >= 8)
        or any("distress" in c.lower() or "diaphoret" in c.lower() for c in (patient.observed_cues or []))
        or patient.first_time_patient
    ):
        action = "ESCALATE"
        if base_priority == "LOW":
            final_priority = "REVIEW"
        explanation_parts.append(
            f"Incomplete intake data ({completeness}%) with active clinical cues. Missing vital signs prevented definitive scoring; escalated for immediate clinician review."
        )

    # Rule 5: Clinical presentation with cardiac/chest discomfort flags -> Minimum baseline MODERATE
    elif base_priority == "LOW" and (
        "chest" in (patient.chief_complaint or "").lower()
        or "cardiac" in (patient.chief_complaint or "").lower()
    ):
        final_priority = "MODERATE"
        action = "RECOMMEND"
        explanation_parts.append(
            f"Risk estimate {risk_score}/100 from {source_label}. Clinical complaint indicates moderate cardiac/chest symptom monitoring required on 15m reassessment schedule."
        )

    # Rule 6: Standard safe recommendation
    else:
        action = "RECOMMEND"
        explanation_parts.append(
            f"Risk estimate {risk_score}/100 from {source_label} on {profile} profile. Workflow confidence is {confidence}%."
        )

    full_explanation = " ".join(explanation_parts)

    return TriageDecisionResult(
        risk_score=risk_score,
        confidence_score=confidence,
        data_completeness=completeness,
        priority=final_priority,
        action=action,
        safety_flags=safety_flags,
        key_signals=all_signals,
        missing_information=missing_info,
        explanation=full_explanation,
        population_profile=profile,
        uncertainty_details=uncertainty.to_dict(),
        model_details=ml_output,
        model_status=model_status,
        model_available=model_available,
        model_source=model_source,
        model_version=model_version
    )
