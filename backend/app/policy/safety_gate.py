"""
Safety Gate and Clinical Conflict Detector (AcuityGuard).
Detects critical vital thresholds, red flags, and conflicting observations.
TODO: CLINICAL VALIDATION REQUIRED.
"""

from typing import Tuple, List, Optional
from app.core.config import settings
from app.models.entities import Patient, Observation

def evaluate_safety_gate(patient: Patient, latest_obs: Optional[Observation]) -> Tuple[List[str], bool, List[str], List[str]]:
    """
    Evaluates safety conditions.
    Returns:
      (safety_flags, has_conflict, conflict_reasons, key_signals)
    """
    safety_flags = []
    conflict_reasons = []
    key_signals = []
    has_conflict = False

    profile = patient.population_profile or "adult"
    thresholds = settings.VITAL_THRESHOLDS.get(profile, settings.VITAL_THRESHOLDS["adult"])

    # 1. Evaluate Vitals against Profile Thresholds
    if latest_obs:
        hr = latest_obs.heart_rate
        rr = latest_obs.respiratory_rate
        sbp = latest_obs.systolic_bp
        spo2 = latest_obs.spo2
        temp = latest_obs.temperature_c

        # Heart Rate
        if hr is not None:
            if hr >= thresholds["hr_critical_high"]:
                safety_flags.append(f"Critical Tachycardia: HR {hr} bpm (>= {thresholds['hr_critical_high']})")
                key_signals.append(f"Severe tachycardia ({hr} bpm)")
            elif hr <= thresholds["hr_critical_low"]:
                safety_flags.append(f"Critical Bradycardia: HR {hr} bpm (<= {thresholds['hr_critical_low']})")
                key_signals.append(f"Severe bradycardia ({hr} bpm)")
            elif hr >= thresholds["hr_warning_high"]:
                key_signals.append(f"Elevated heart rate ({hr} bpm)")
            elif hr <= thresholds["hr_warning_low"]:
                key_signals.append(f"Low heart rate ({hr} bpm)")

        # Respiratory Rate
        if rr is not None:
            if rr >= thresholds["rr_critical_high"]:
                safety_flags.append(f"Critical Tachypnea: RR {rr}/min (>= {thresholds['rr_critical_high']})")
                key_signals.append(f"Severe respiratory distress ({rr}/min)")
            elif rr <= thresholds["rr_critical_low"]:
                safety_flags.append(f"Critical Bradypnea: RR {rr}/min (<= {thresholds['rr_critical_low']})")
                key_signals.append(f"Severe hypoventilation ({rr}/min)")
            elif rr >= thresholds["rr_warning_high"]:
                key_signals.append(f"Elevated respiratory rate ({rr}/min)")

        # SpO2
        if spo2 is not None:
            if spo2 <= thresholds["spo2_critical_low"]:
                safety_flags.append(f"Critical Hypoxia: SpO2 {spo2}% (<= {thresholds['spo2_critical_low']}%)")
                key_signals.append(f"Severe hypoxia ({spo2}%)")
            elif spo2 <= thresholds["spo2_warning_low"]:
                key_signals.append(f"Borderline oxygen saturation ({spo2}%)")

        # Blood Pressure
        if sbp is not None:
            if sbp >= thresholds["sys_bp_critical_high"]:
                safety_flags.append(f"Hypertensive Crisis Risk: Systolic BP {sbp} mmHg")
                key_signals.append(f"Severe hypertension ({sbp} mmHg)")
            elif sbp <= thresholds["sys_bp_critical_low"]:
                safety_flags.append(f"Critical Hypotension / Shock Risk: Systolic BP {sbp} mmHg")
                key_signals.append(f"Severe hypotension ({sbp} mmHg)")
            elif sbp <= thresholds["sys_bp_warning_low"]:
                key_signals.append(f"Low systolic BP ({sbp} mmHg)")

        # Temperature
        if temp is not None:
            if temp >= thresholds["temp_critical_high"]:
                safety_flags.append(f"Hyperpyrexia: Temp {temp}°C")
                key_signals.append(f"High fever ({temp}°C)")
            elif temp <= thresholds["temp_warning_low"]:
                safety_flags.append(f"Hypothermia: Temp {temp}°C")
                key_signals.append(f"Hypothermia ({temp}°C)")

    # 2. Check for Red Flags in Presentation & Cues
    cues = [c.lower() for c in (patient.observed_cues or [])]
    complaint = (patient.chief_complaint or "").lower()
    symptoms = (patient.symptom_text or "").lower()

    if any("unresponsive" in c or "lethargic" in c for c in cues) or "unresponsive" in symptoms:
        safety_flags.append("Altered Mental Status / Lethargy flagged in observation cues")
        key_signals.append("Altered mental status")

    if any("cyanot" in c for c in cues):
        key_signals.append("Cyanotic presentation observed")

    if any("diaphoret" in c for c in cues):
        key_signals.append("Diaphoresis observed")

    if patient.pain_score is not None and patient.pain_score >= 8:
        key_signals.append(f"Severe reported pain ({patient.pain_score}/10)")

    # 3. Detect Conflicting Clinical Inputs
    # Example from spec: SpO2 >= 98% while cyanotic appearance is observed
    if latest_obs and latest_obs.spo2 is not None and latest_obs.spo2 >= 98.0:
        if any("cyanot" in c for c in cues) or "cyanosis" in symptoms:
            has_conflict = True
            conflict_reasons.append("Observation conflict: High recorded SpO2 (>= 98%) contradicts observed cyanotic presentation.")

    return safety_flags, has_conflict, conflict_reasons, key_signals
