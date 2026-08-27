"""
Synthetic Dataset Seeder (24 Cases).
Strictly matches docs/TEST_CASES.md.
All names, vitals, and narratives are purely synthetic and fictional.
"""

from datetime import datetime, timezone, timedelta
from typing import List
from sqlalchemy.orm import Session
from app.models.entities import Patient, Observation, TriageResult, ClinicianDecision, AuditEvent
from app.policy.action_policy import evaluate_patient_triage
from app.reassessment.monitor import reassessment_monitor

def get_seed_patients_data() -> List[dict]:
    now = datetime.now(timezone.utc)
    return [
        {
            "patient_id": "PT-001",
            "name": "Patient Alpha (Synthetic)",
            "age_years": 32,
            "population_profile": "adult",
            "sex": "Male",
            "arrival_mode": "walk_in",
            "first_time_patient": False,
            "history_available": True,
            "known_conditions": ["Asthma (mild)"],
            "chief_complaint": "Ankle sprain after running",
            "symptom_text": "Twisted right ankle 2 hours ago. Mild localized swelling, weight bearing with mild pain.",
            "symptom_duration_minutes": 120,
            "pain_score": 4.0,
            "observed_cues": ["Normal gait with mild limp"],
            "waiting_minutes": 25,
            "vitals": [{"hr": 74, "rr": 16, "sbp": 122, "dbp": 78, "spo2": 99.0, "temp": 36.8}]
        },
        {
            "patient_id": "PT-002",
            "name": "Patient Beta (Synthetic)",
            "age_years": 41,
            "population_profile": "adult",
            "sex": "Female",
            "arrival_mode": "walk_in",
            "first_time_patient": False,
            "history_available": True,
            "known_conditions": ["None"],
            "chief_complaint": "Minor superficial forearm laceration",
            "symptom_text": "Clean kitchen knife cut on left forearm. Bleeding controlled with pressure.",
            "symptom_duration_minutes": 45,
            "pain_score": 3.0,
            "observed_cues": ["Calm, alert"],
            "waiting_minutes": 15,
            "vitals": [{"hr": 78, "rr": 15, "sbp": 118, "dbp": 76, "spo2": 98.0, "temp": 36.6}]
        },
        {
            "patient_id": "PT-003",
            "name": "Patient Gamma (Synthetic)",
            "age_years": 54,
            "population_profile": "adult",
            "sex": "Male",
            "arrival_mode": "walk_in",
            "first_time_patient": False,
            "history_available": False,
            "known_conditions": [],
            "chief_complaint": "Substernal chest tightness",
            "symptom_text": "Intermittent retrosternal pressure radiating to left shoulder for 90 minutes. Mild shortness of breath.",
            "symptom_duration_minutes": 90,
            "pain_score": 7.0,
            "observed_cues": ["Diaphoretic", "Anxious"],
            "waiting_minutes": 10,
            "vitals": [{"hr": 104, "rr": 22, "sbp": 152, "dbp": 94, "spo2": 95.0, "temp": 37.1}]
        },
        {
            "patient_id": "PT-004",
            "name": "Patient Delta (Synthetic)",
            "age_years": 28,
            "population_profile": "adult",
            "sex": "Female",
            "arrival_mode": "walk_in",
            "first_time_patient": False,
            "history_available": True,
            "known_conditions": ["Gastritis"],
            "chief_complaint": "Right lower quadrant abdominal pain",
            "symptom_text": "Cramping lower abdominal discomfort since morning. Mild nausea, no vomiting.",
            "symptom_duration_minutes": 360,
            "pain_score": 6.0,
            "observed_cues": ["Guarding abdomen"],
            "waiting_minutes": 30,
            "vitals": [{"hr": 88, "rr": 18, "sbp": 126, "dbp": 82, "spo2": 98.0, "temp": 37.8}]
        },
        {
            "patient_id": "PT-005",
            "name": "Patient Epsilon (Synthetic - Zero History)",
            "age_years": 47,
            "population_profile": "adult",
            "sex": "Male",
            "arrival_mode": "walk_in",
            "first_time_patient": True,
            "history_available": False,
            "known_conditions": [],
            "chief_complaint": "Generalized weakness and malaise",
            "symptom_text": "First-time attendee with no previous medical history. Feeling dizzy and profoundly fatigued for 3 days.",
            "symptom_duration_minutes": 4320,
            "pain_score": 2.0,
            "observed_cues": ["Pale conjunctiva"],
            "waiting_minutes": 20,
            "vitals": [{"hr": 92, "rr": 18, "sbp": 108, "dbp": 68, "spo2": 96.0, "temp": 37.0}]
        },
        {
            "patient_id": "PT-006",
            "name": "Patient Zeta (Synthetic - Ambiguous)",
            "age_years": 39,
            "population_profile": "adult",
            "sex": "Female",
            "arrival_mode": "walk_in",
            "first_time_patient": False,
            "history_available": False,
            "known_conditions": [],
            "chief_complaint": "Postural dizziness and palpitations",
            "symptom_text": "Dizzy upon standing, accompanied by feeling heart racing. Unclear onset.",
            "symptom_duration_minutes": 240,
            "pain_score": 1.0,
            "observed_cues": ["Unsteady gait"],
            "waiting_minutes": 35,
            "vitals": [{"hr": 98, "rr": 19, "sbp": 110, "dbp": 70, "spo2": 97.0, "temp": 36.9}]
        },
        {
            "patient_id": "PT-007",
            "name": "Patient Eta (Synthetic)",
            "age_years": 50,
            "population_profile": "adult",
            "sex": "Male",
            "arrival_mode": "walk_in",
            "first_time_patient": False,
            "history_available": True,
            "known_conditions": ["COPD"],
            "chief_complaint": "Productive cough and mild wheezing",
            "symptom_text": "Chronic cough increased past 2 days, moderate yellow sputum, no chest pain.",
            "symptom_duration_minutes": 2880,
            "pain_score": 2.0,
            "observed_cues": ["Audible expiratory wheeze"],
            "waiting_minutes": 40,
            "vitals": [{"hr": 86, "rr": 21, "sbp": 134, "dbp": 86, "spo2": 94.0, "temp": 37.4}]
        },
        {
            "patient_id": "PT-008",
            "name": "Patient Theta (Synthetic)",
            "age_years": 22,
            "population_profile": "adult",
            "sex": "Female",
            "arrival_mode": "walk_in",
            "first_time_patient": False,
            "history_available": True,
            "known_conditions": ["Migraine"],
            "chief_complaint": "Severe unilateral throbbing headache",
            "symptom_text": "Photophobia, nausea, classic migraine attack resembling past episodes.",
            "symptom_duration_minutes": 180,
            "pain_score": 8.0,
            "observed_cues": ["Holding head", "Sensitivity to light"],
            "waiting_minutes": 18,
            "vitals": [{"hr": 82, "rr": 16, "sbp": 120, "dbp": 80, "spo2": 99.0, "temp": 36.7}]
        },
        {
            "patient_id": "PT-009",
            "name": "Patient Iota (Synthetic - Overlapping Ambiguity)",
            "age_years": 61,
            "population_profile": "adult",
            "sex": "Male",
            "arrival_mode": "walk_in",
            "first_time_patient": False,
            "history_available": False,
            "known_conditions": [],
            "chief_complaint": "Epigastric discomfort and clamminess",
            "symptom_text": "Unclear whether cardiac or gastrointestinal etiology; sudden onset after meal.",
            "symptom_duration_minutes": 60,
            "pain_score": 5.0,
            "observed_cues": ["Diaphoretic", "Clammy skin"],
            "waiting_minutes": 12,
            "vitals": [{"hr": 106, "rr": 20, "sbp": 142, "dbp": 88, "spo2": 96.0, "temp": 37.0}]
        },
        {
            "patient_id": "PT-010",
            "name": "Patient Kappa (Synthetic - Deterioration)",
            "age_years": 49,
            "population_profile": "adult",
            "sex": "Female",
            "arrival_mode": "ambulance",
            "first_time_patient": False,
            "history_available": True,
            "known_conditions": ["Type 2 Diabetes"],
            "chief_complaint": "Severe shortness of breath",
            "symptom_text": "Progressive dyspnea over 4 hours with marked work of breathing.",
            "symptom_duration_minutes": 240,
            "pain_score": 4.0,
            "observed_cues": ["Accessory muscle use", "Tachypneic"],
            "waiting_minutes": 25,
            "vitals": [
                {"hr": 98, "rr": 24, "sbp": 130, "dbp": 85, "spo2": 93.0, "temp": 37.5},
                {"hr": 128, "rr": 32, "sbp": 105, "dbp": 65, "spo2": 88.0, "temp": 37.9}
            ]
        },
        {
            "patient_id": "PT-011",
            "name": "Patient Lambda (Synthetic - Pediatric)",
            "age_years": 4,
            "population_profile": "pediatric",
            "sex": "Female",
            "arrival_mode": "walk_in",
            "first_time_patient": True,
            "history_available": False,
            "known_conditions": [],
            "chief_complaint": "High fever and lethargy in toddler",
            "symptom_text": "Parent reports child is unusually drowsy, poor fluid intake for 24h, warm to touch.",
            "symptom_duration_minutes": 1440,
            "pain_score": None,
            "observed_cues": ["Lethargic", "Dry mucous membranes"],
            "waiting_minutes": 15,
            "vitals": [{"hr": 148, "rr": 36, "sbp": 92, "dbp": 58, "spo2": 95.0, "temp": 39.2}]
        },
        {
            "patient_id": "PT-012",
            "name": "Patient Mu (Synthetic - Pediatric)",
            "age_years": 8,
            "population_profile": "pediatric",
            "sex": "Male",
            "arrival_mode": "walk_in",
            "first_time_patient": False,
            "history_available": True,
            "known_conditions": ["None"],
            "chief_complaint": "Closed forearm injury after fall",
            "symptom_text": "Fell off bicycle onto outstretched hand. Visible deformity of right distal forearm, neurovascularly intact.",
            "symptom_duration_minutes": 60,
            "pain_score": 6.0,
            "observed_cues": ["Crying with pain", "Holding forearm"],
            "waiting_minutes": 20,
            "vitals": [{"hr": 102, "rr": 22, "sbp": 104, "dbp": 66, "spo2": 99.0, "temp": 36.8}]
        },
        {
            "patient_id": "PT-013",
            "name": "Patient Nu (Synthetic - Pediatric)",
            "age_years": 2,
            "population_profile": "pediatric",
            "sex": "Male",
            "arrival_mode": "walk_in",
            "first_time_patient": False,
            "history_available": False,
            "known_conditions": [],
            "chief_complaint": "Barking cough and stridor",
            "symptom_text": "Sudden onset barking cough at night with inspiratory noise at rest.",
            "symptom_duration_minutes": 180,
            "pain_score": None,
            "observed_cues": ["Inspiratory stridor", "Subcostal retractions"],
            "waiting_minutes": 10,
            "vitals": [{"hr": 138, "rr": 34, "sbp": 88, "dbp": 54, "spo2": 94.0, "temp": 38.3}]
        },
        {
            "patient_id": "PT-014",
            "name": "Patient Xi (Synthetic - Pediatric Zero History)",
            "age_years": 1,
            "population_profile": "pediatric",
            "sex": "Female",
            "arrival_mode": "walk_in",
            "first_time_patient": True,
            "history_available": False,
            "known_conditions": [],
            "chief_complaint": "Repeated vomiting and drowsiness",
            "symptom_text": "Infant vomiting all oral intake for 12 hours. Very sleepy, sunken eyes.",
            "symptom_duration_minutes": 720,
            "pain_score": None,
            "observed_cues": ["Lethargic", "Delayed capillary refill"],
            "waiting_minutes": 8,
            "vitals": [{"hr": 158, "rr": 38, "sbp": 78, "dbp": 46, "spo2": 95.0, "temp": 38.8}]
        },
        {
            "patient_id": "PT-015",
            "name": "Patient Omicron (Synthetic - Geriatric)",
            "age_years": 78,
            "population_profile": "geriatric",
            "sex": "Female",
            "arrival_mode": "walk_in",
            "first_time_patient": False,
            "history_available": True,
            "known_conditions": ["Hypertension", "Osteoarthritis"],
            "chief_complaint": "Generalized weakness and slow decline",
            "symptom_text": "Difficulty walking over past week, decreased appetite, no focal neurological deficit.",
            "symptom_duration_minutes": 10080,
            "pain_score": 3.0,
            "observed_cues": ["Frail", "Wheelchair user"],
            "waiting_minutes": 45,
            "vitals": [{"hr": 76, "rr": 18, "sbp": 142, "dbp": 82, "spo2": 95.0, "temp": 36.4}]
        },
        {
            "patient_id": "PT-016",
            "name": "Patient Pi (Synthetic - Geriatric)",
            "age_years": 82,
            "population_profile": "geriatric",
            "sex": "Male",
            "arrival_mode": "walk_in",
            "first_time_patient": False,
            "history_available": False,
            "known_conditions": [],
            "chief_complaint": "Near-syncope and lightheadedness",
            "symptom_text": "Episode of near-blackout while seated. Incomplete medical history available.",
            "symptom_duration_minutes": 120,
            "pain_score": 0.0,
            "observed_cues": ["Pale", "Slow responses"],
            "waiting_minutes": 22,
            "vitals": [{"hr": 52, "rr": 17, "sbp": 98, "dbp": 60, "spo2": 94.0, "temp": 36.1}]
        },
        {
            "patient_id": "PT-017",
            "name": "Patient Rho (Synthetic - Geriatric Ambiguity)",
            "age_years": 85,
            "population_profile": "geriatric",
            "sex": "Female",
            "arrival_mode": "walk_in",
            "first_time_patient": True,
            "history_available": False,
            "known_conditions": [],
            "chief_complaint": "Acute confusion and weakness",
            "symptom_text": "Family brought patient due to sudden disorientation, wandering, and weakness. No records found.",
            "symptom_duration_minutes": 360,
            "pain_score": None,
            "observed_cues": ["Disoriented to time and place"],
            "waiting_minutes": 15,
            "vitals": [{"hr": 96, "rr": 20, "sbp": 138, "dbp": 78, "spo2": 93.0, "temp": 37.7}]
        },
        {
            "patient_id": "PT-018",
            "name": "Patient Sigma (Synthetic - Geriatric)",
            "age_years": 72,
            "population_profile": "geriatric",
            "sex": "Male",
            "arrival_mode": "walk_in",
            "first_time_patient": False,
            "history_available": True,
            "known_conditions": ["Congestive Heart Failure"],
            "chief_complaint": "Mild bilateral leg edema and dyspnea on exertion",
            "symptom_text": "Gradual increase in ankle swelling over 2 weeks, breathlessness when climbing stairs.",
            "symptom_duration_minutes": 20160,
            "pain_score": 1.0,
            "observed_cues": ["Pitting edema to mid-calf"],
            "waiting_minutes": 50,
            "vitals": [{"hr": 84, "rr": 19, "sbp": 136, "dbp": 84, "spo2": 95.0, "temp": 36.6}]
        },
        {
            "patient_id": "PT-019",
            "name": "Patient Tau (Synthetic - Clinical Conflict)",
            "age_years": 34,
            "population_profile": "adult",
            "sex": "Male",
            "arrival_mode": "walk_in",
            "first_time_patient": False,
            "history_available": True,
            "known_conditions": ["None"],
            "chief_complaint": "Shortness of breath with blue lips",
            "symptom_text": "Patient appears cyanotic around lips and nail beds, yet fingertip pulse oximeter shows 99%.",
            "symptom_duration_minutes": 60,
            "pain_score": 2.0,
            "observed_cues": ["Cyanotic appearance", "Peripheral cyanosis"],
            "waiting_minutes": 10,
            "vitals": [{"hr": 92, "rr": 24, "sbp": 128, "dbp": 82, "spo2": 99.0, "temp": 36.8}]
        },
        {
            "patient_id": "PT-020",
            "name": "Patient Upsilon (Synthetic - Stale Vitals)",
            "age_years": 45,
            "population_profile": "adult",
            "sex": "Female",
            "arrival_mode": "walk_in",
            "first_time_patient": False,
            "history_available": False,
            "known_conditions": ["Asthma"],
            "chief_complaint": "Moderate wheezing and chest tightness",
            "symptom_text": "Intake vitals recorded 90 minutes ago without update. Feeling increasingly tight.",
            "symptom_duration_minutes": 180,
            "pain_score": 4.0,
            "observed_cues": ["Expiratory wheeze"],
            "waiting_minutes": 95,
            "vitals": [{"hr": 94, "rr": 23, "sbp": 132, "dbp": 84, "spo2": 94.0, "temp": 37.2}]
        },
        {
            "patient_id": "PT-021",
            "name": "Patient Phi (Synthetic - Killer Demo Deterioration)",
            "age_years": 58,
            "population_profile": "adult",
            "sex": "Male",
            "arrival_mode": "walk_in",
            "first_time_patient": False,
            "history_available": True,
            "known_conditions": ["Hypertension"],
            "chief_complaint": "Moderate chest discomfort and dizziness",
            "symptom_text": "Started with mild dull ache 2 hours ago. Recently worsened with sweating.",
            "symptom_duration_minutes": 120,
            "pain_score": 5.0,
            "observed_cues": ["Pale"],
            "waiting_minutes": 28,
            "vitals": [
                {"hr": 86, "rr": 18, "sbp": 138, "dbp": 88, "spo2": 96.0, "temp": 36.9},
                {"hr": 118, "rr": 26, "sbp": 98, "dbp": 62, "spo2": 91.0, "temp": 37.3}
            ]
        },
        {
            "patient_id": "PT-022",
            "name": "Patient Chi (Synthetic - Sparse Intake)",
            "age_years": 29,
            "population_profile": "adult",
            "sex": "Female",
            "arrival_mode": "walk_in",
            "first_time_patient": True,
            "history_available": False,
            "known_conditions": [],
            "chief_complaint": "Severe abdominal cramping",
            "symptom_text": "Patient walked in clutching stomach. Rapid verbal intake only; full vitals pending.",
            "symptom_duration_minutes": 45,
            "pain_score": 9.0,
            "observed_cues": ["Severe distress", "Diaphoretic"],
            "waiting_minutes": 12,
            "vitals": [{"hr": 110, "rr": None, "sbp": None, "dbp": None, "spo2": None, "temp": None}]
        },
        {
            "patient_id": "PT-023",
            "name": "Patient Psi (Synthetic - Pediatric Queue Monitor)",
            "age_years": 6,
            "population_profile": "pediatric",
            "sex": "Female",
            "arrival_mode": "walk_in",
            "first_time_patient": False,
            "history_available": False,
            "known_conditions": [],
            "chief_complaint": "Fever and persistent ear pain",
            "symptom_text": "Earache past 24h, high fever, fussy, pulling at left ear.",
            "symptom_duration_minutes": 1440,
            "pain_score": 7.0,
            "observed_cues": ["Irritable", "Flushed face"],
            "waiting_minutes": 55,
            "vitals": [{"hr": 125, "rr": 24, "sbp": 100, "dbp": 62, "spo2": 97.0, "temp": 38.9}]
        },
        {
            "patient_id": "PT-024",
            "name": "Patient Omega (Synthetic - Geriatric Overdue)",
            "age_years": 79,
            "population_profile": "geriatric",
            "sex": "Male",
            "arrival_mode": "walk_in",
            "first_time_patient": False,
            "history_available": False,
            "known_conditions": ["Hypertension", "Atrial Fibrillation"],
            "chief_complaint": "Irregular heartbeat and breathlessness",
            "symptom_text": "Heart fluttering sensation, mild dyspnea on sitting, waiting past scheduled reassessment window.",
            "symptom_duration_minutes": 300,
            "pain_score": 2.0,
            "observed_cues": ["Irregular pulse noted"],
            "waiting_minutes": 70,
            "vitals": [{"hr": 115, "rr": 22, "sbp": 148, "dbp": 92, "spo2": 94.0, "temp": 36.7}]
        }
    ]

def seed_database(db: Session):
    """Populates the database with 24 test cases and generates initial evaluation results."""
    # Check if patients already exist
    if db.query(Patient).count() > 0:
        return

    data = get_seed_patients_data()
    now = datetime.now(timezone.utc)

    for item in data:
        patient = Patient(
            patient_id=item["patient_id"],
            name=item["name"],
            age_years=item["age_years"],
            population_profile=item["population_profile"],
            sex=item["sex"],
            arrival_mode=item["arrival_mode"],
            first_time_patient=item["first_time_patient"],
            history_available=item["history_available"],
            known_conditions=item["known_conditions"],
            chief_complaint=item["chief_complaint"],
            symptom_text=item["symptom_text"],
            symptom_duration_minutes=item["symptom_duration_minutes"],
            pain_score=item["pain_score"],
            observed_cues=item["observed_cues"],
            arrival_time=now - timedelta(minutes=item["waiting_minutes"]),
            waiting_minutes=item["waiting_minutes"],
            current_status="WAITING"
        )
        db.add(patient)
        db.flush()

        # Add observations
        vitals_list = item.get("vitals", [])
        created_obs = []
        for idx, v in enumerate(vitals_list):
            obs_time = now - timedelta(minutes=max(0, item["waiting_minutes"] - (idx * 15)))
            obs = Observation(
                observation_id=f"OBS-{item['patient_id']}-{idx+1}",
                patient_id=item["patient_id"],
                timestamp=obs_time,
                heart_rate=v.get("hr"),
                respiratory_rate=v.get("rr"),
                systolic_bp=v.get("sbp"),
                diastolic_bp=v.get("dbp"),
                spo2=v.get("spo2"),
                temperature_c=v.get("temp"),
                measurement_source="device",
                observation_notes="Initial intake vitals" if idx == 0 else "Updated timeline vitals"
            )
            db.add(obs)
            created_obs.append(obs)
        db.flush()

        # Run Initial Triage Evaluation
        latest_obs = created_obs[-1] if created_obs else None
        eval_result = evaluate_patient_triage(patient, latest_obs)

        # Update patient status
        patient.current_priority = eval_result.priority
        patient.current_action = eval_result.action
        patient.current_confidence = eval_result.confidence_score
        patient.current_risk_score = eval_result.risk_score

        # Check reassessment status
        needs_reassess, reasons, _ = reassessment_monitor.evaluate_patient_reassessment(patient)
        patient.needs_reassessment = needs_reassess
        patient.reassessment_reasons = reasons

        # Save Triage Result
        triage_record = TriageResult(
            result_id=f"TR-{item['patient_id']}-1",
            patient_id=item["patient_id"],
            timestamp=now - timedelta(minutes=item["waiting_minutes"]),
            risk_score=eval_result.risk_score,
            confidence_score=eval_result.confidence_score,
            data_completeness=eval_result.data_completeness,
            priority=eval_result.priority,
            action=eval_result.action,
            safety_flags=eval_result.safety_flags,
            key_signals=eval_result.key_signals,
            missing_information=eval_result.missing_information,
            explanation=eval_result.explanation,
            population_profile=eval_result.population_profile
        )
        db.add(triage_record)

        # Add initial Audit Event
        audit = AuditEvent(
            audit_id=f"AUD-{item['patient_id']}-INIT",
            timestamp=now - timedelta(minutes=item["waiting_minutes"]),
            actor_id="system",
            actor_role="system",
            event_type="triage",
            patient_id=item["patient_id"],
            recommendation=eval_result.priority,
            confidence=eval_result.confidence_score,
            decision=eval_result.action,
            details={"completeness": eval_result.data_completeness, "signals": eval_result.key_signals}
        )
        db.add(audit)

    db.commit()
