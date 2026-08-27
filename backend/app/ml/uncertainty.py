"""
Uncertainty and Workflow Confidence Subsystem.
Computes a transparent composite workflow confidence indicator from:
1. Model certainty (calibrated probability margin from decision boundary)
2. Data completeness / reliability
3. Input consistency
4. Population-profile support
TODO: CLINICAL VALIDATION REQUIRED.
"""

from typing import Dict, Any, List, Optional
from app.models.entities import Patient, Observation

class UncertaintyBreakdown:
    def __init__(
        self,
        workflow_confidence: float,
        model_certainty: float,
        data_reliability: float,
        consistency_score: float,
        profile_support_score: float,
        contributing_factors: List[str]
    ):
        self.workflow_confidence = workflow_confidence
        self.model_certainty = model_certainty
        self.data_reliability = data_reliability
        self.consistency_score = consistency_score
        self.profile_support_score = profile_support_score
        self.contributing_factors = contributing_factors

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_confidence": self.workflow_confidence,
            "model_certainty": self.model_certainty,
            "data_reliability": self.data_reliability,
            "consistency": self.consistency_score,
            "profile_support": self.profile_support_score,
            "contributing_factors": self.contributing_factors
        }

def compute_uncertainty_breakdown(
    patient: Patient,
    latest_obs: Optional[Observation],
    calibrated_prob: float,
    completeness: float,
    has_conflict: bool
) -> UncertaintyBreakdown:
    """
    Computes a composite workflow confidence indicator.
    Does NOT claim to be a clinical probability of truth.
    """
    factors = []

    # 1. Model Certainty (Distance from decision boundary 0.5)
    # Range 0..100. If prob is 0.95 or 0.05 -> certainty 90%. If prob is 0.50 -> certainty 0%.
    prob_dist = abs(calibrated_prob - 0.5)
    model_certainty = round(min(100.0, prob_dist * 200.0), 1)
    if model_certainty < 40.0:
        factors.append(f"Model uncertainty elevated: Calibrated probability ({round(calibrated_prob, 2)}) is close to classification threshold (0.50).")

    # 2. Data Reliability (Completeness)
    data_reliability = round(completeness, 1)
    if data_reliability < 65.0:
        factors.append(f"Incomplete intake information: Data completeness is {data_reliability}%.")

    # 3. Consistency
    consistency_score = 95.0
    if has_conflict:
        consistency_score = 15.0
        factors.append("Critical contradiction flagged between physiological observation and clinical cues.")
    else:
        # Check for ambiguity in cues / narrative
        symptom_text = (patient.symptom_text or "").lower()
        cues = [c.lower() for c in (patient.observed_cues or [])]
        if any(w in symptom_text or any(w in c for c in cues) for w in ["dizziness", "confusion", "unclear", "malaise"]):
            consistency_score -= 20.0
            factors.append("Presentation contains ambiguous or non-specific clinical symptoms.")

    # 4. Population-Profile Support
    profile_support_score = 95.0
    if patient.first_time_patient or not patient.history_available:
        profile_support_score -= 25.0
        factors.append("First-time presentation: Absence of historical baseline reduces longitudinal profile certainty.")

    if patient.population_profile == "pediatric" and (patient.age_years is not None and patient.age_years < 2):
        profile_support_score -= 15.0
        factors.append("Infant presentation: Higher physiological volatility increases uncertainty threshold.")
    elif patient.population_profile == "geriatric" and (patient.age_years is not None and patient.age_years >= 80):
        profile_support_score -= 15.0
        factors.append("Advanced geriatric presentation: Multi-morbidity risk increases uncertainty threshold.")

    # 5. Composite Workflow Confidence
    # Weights: Model Certainty (35%), Data Reliability (35%), Consistency (15%), Profile Support (15%)
    composite = (
        (0.35 * model_certainty) +
        (0.35 * data_reliability) +
        (0.15 * consistency_score) +
        (0.15 * profile_support_score)
    )

    final_confidence = round(max(15.0, min(95.0, composite)), 1)

    return UncertaintyBreakdown(
        workflow_confidence=final_confidence,
        model_certainty=model_certainty,
        data_reliability=data_reliability,
        consistency_score=consistency_score,
        profile_support_score=profile_support_score,
        contributing_factors=factors
    )
