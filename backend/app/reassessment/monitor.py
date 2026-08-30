"""
Continuous Queue Monitoring and Reassessment Engine (AcuityWatch).
Evaluates wait times, vital deterioration trends, and risk trajectory shifts.
TODO: CLINICAL VALIDATION REQUIRED.
"""

from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timezone
from app.core.config import settings
from app.models.entities import Patient, Observation

class ReassessmentMonitor:
    @staticmethod
    def evaluate_patient_reassessment(patient: Patient) -> Tuple[bool, List[str], int]:
        """
        Evaluates whether a waiting patient requires reassessment and assigns an operational attention score.
        Surge Operational Attention Hierarchy:
          Tier 1: Deteriorating (+1000)
          Tier 2: Reassessment Overdue (+500)
          Tier 3: Low Confidence / High Uncertainty (+300)
          Tier 4: High Priority (+150 for IMMEDIATE, +120 for HIGH)
          Tier 5: Moderate / Low (+40 for MODERATE, +10 for LOW)
        Returns:
            (needs_reassessment: bool, reasons: List[str], attention_score: int)
        """
        reasons = []
        needs_reassessment = False
        attention_score = 0

        # Base Priority Weight
        priority_weights = {
            "IMMEDIATE": 150,
            "HIGH": 120,
            "MODERATE": 40,
            "LOW": 10,
            "REVIEW": 80
        }
        attention_score += priority_weights.get(patient.current_priority, 10)

        # 1. Wait Time Trigger
        wait_mins = patient.waiting_minutes or 0
        max_wait = settings.REASSESSMENT_WINDOWS_MINUTES.get(patient.current_priority, 60)
        if wait_mins > max_wait:
            needs_reassessment = True
            reasons.append(f"Overdue for clinical reassessment: Waiting {wait_mins}m (policy window is {max_wait}m)")
            attention_score += 500

        # 2. Vital-Change Deterioration Trigger
        # Compare newest observation with previous observation
        def _get_ts(obs: Observation):
            if obs.timestamp is None:
                return datetime.min.replace(tzinfo=None)
            if obs.timestamp.tzinfo is not None:
                return obs.timestamp.astimezone(timezone.utc).replace(tzinfo=None)
            return obs.timestamp

        obs_list = sorted(patient.observations, key=_get_ts, reverse=True)
        if len(obs_list) >= 2:
            latest = obs_list[0]
            prev = obs_list[1]
            
            # Check SpO2 drop
            if latest.spo2 is not None and prev.spo2 is not None:
                if (prev.spo2 - latest.spo2) >= 4.0:
                    needs_reassessment = True
                    reasons.append(f"Deterioration: SpO2 dropped from {prev.spo2}% to {latest.spo2}% (-{round(prev.spo2 - latest.spo2, 1)}%)")
                    attention_score += 1000

            # Check HR increase
            if latest.heart_rate is not None and prev.heart_rate is not None:
                if (latest.heart_rate - prev.heart_rate) >= 25.0:
                    needs_reassessment = True
                    reasons.append(f"Deterioration: Heart rate spiked from {prev.heart_rate} to {latest.heart_rate} bpm (+{round(latest.heart_rate - prev.heart_rate, 1)} bpm)")
                    attention_score += 900

            # Check BP drop (Systolic)
            if latest.systolic_bp is not None and prev.systolic_bp is not None:
                if (prev.systolic_bp - latest.systolic_bp) >= 25.0:
                    needs_reassessment = True
                    reasons.append(f"Deterioration: Systolic BP fell from {prev.systolic_bp} to {latest.systolic_bp} mmHg (-{round(prev.systolic_bp - latest.systolic_bp, 1)} mmHg)")
                    attention_score += 900

            # Check RR increase
            if latest.respiratory_rate is not None and prev.respiratory_rate is not None:
                if (latest.respiratory_rate - prev.respiratory_rate) >= 6.0:
                    needs_reassessment = True
                    reasons.append(f"Deterioration: Respiratory rate increased from {prev.respiratory_rate} to {latest.respiratory_rate}/min")
                    attention_score += 800

        # 3. Uncertainty Trigger
        conf = patient.current_confidence if patient.current_confidence is not None else 75.0
        if conf < settings.MIN_CONFIDENCE_THRESHOLD and wait_mins >= 15:
            needs_reassessment = True
            reasons.append(f"Uncertainty flag: Patient has remained with low confidence ({conf}%) for {wait_mins}m")
            attention_score += 300

        # Tie-breaker: longer wait time gets higher attention within the same tier
        attention_score += min(50, wait_mins)

        if needs_reassessment:
            attention_score += 30

        return needs_reassessment, reasons, attention_score

reassessment_monitor = ReassessmentMonitor()
