"""
Synthetic Data Generation Pipeline for AcuityFlow AI ML Baseline.
Generates 2,500 synthetic patient encounters for ML training and evaluation.
Fixed random seed ensures reproducibility.
IMPORTANT: Labels are synthetic demonstration labels and are NOT clinical outcomes.
"""

import os
import random
import numpy as np
import pandas as pd

def generate_synthetic_cohort(num_samples: int = 2500, random_seed: int = 42) -> pd.DataFrame:
    np.random.seed(random_seed)
    random.seed(random_seed)

    records = []
    
    for i in range(num_samples):
        patient_id = f"SYN-{i+1:05d}"
        
        # 1. Demographic profile selection
        profile_choice = np.random.choice(["pediatric", "adult", "geriatric"], p=[0.25, 0.50, 0.25])
        
        if profile_choice == "pediatric":
            age = int(np.random.randint(1, 18))
            sex = np.random.choice(["Male", "Female"])
            # Pediatric baseline vitals
            hr = float(np.random.normal(110, 22))
            rr = float(np.random.normal(26, 7))
            sbp = float(np.random.normal(100, 14))
            dbp = float(np.random.normal(62, 10))
            spo2 = float(np.clip(np.random.normal(97.5, 2.5), 82.0, 100.0))
            temp = float(np.random.normal(37.2, 0.9))
        elif profile_choice == "geriatric":
            age = int(np.random.randint(65, 95))
            sex = np.random.choice(["Male", "Female"])
            # Geriatric baseline vitals
            hr = float(np.random.normal(78, 16))
            rr = float(np.random.normal(18, 5))
            sbp = float(np.random.normal(136, 22))
            dbp = float(np.random.normal(82, 12))
            spo2 = float(np.clip(np.random.normal(95.5, 3.2), 80.0, 100.0))
            temp = float(np.random.normal(36.6, 0.7))
        else:
            age = int(np.random.randint(18, 65))
            sex = np.random.choice(["Male", "Female"])
            # Adult baseline vitals
            hr = float(np.random.normal(76, 15))
            rr = float(np.random.normal(16, 4))
            sbp = float(np.random.normal(122, 16))
            dbp = float(np.random.normal(78, 10))
            spo2 = float(np.clip(np.random.normal(98.0, 2.0), 84.0, 100.0))
            temp = float(np.random.normal(36.8, 0.6))

        # 2. History status
        hist_status = np.random.choice(["full", "partial", "none"], p=[0.60, 0.25, 0.15])
        history_available = hist_status != "none"
        first_time_patient = hist_status == "none"

        # 3. Chief complaints & symptom features
        complaint_pool = [
            ("Chest pain", 0.7),
            ("Shortness of breath", 0.65),
            ("Abdominal pain", 0.4),
            ("Fever and lethargy", 0.5),
            ("Headache", 0.3),
            ("Dizziness", 0.35),
            ("Weakness", 0.35),
            ("Laceration / Injury", 0.2),
            ("Ankle sprain", 0.1),
            ("Cough and wheeze", 0.35)
        ]
        complaint, complaint_risk_weight = complaint_pool[np.random.randint(len(complaint_pool))]
        
        pain_score = float(np.random.randint(0, 11)) if np.random.rand() > 0.15 else None
        symptom_duration = int(np.random.choice([15, 30, 60, 120, 240, 720, 1440, 2880]))

        # 4. Injected Controlled Missingness
        # Some encounters have missing measurements
        if np.random.rand() < 0.08:
            temp = None
        if np.random.rand() < 0.06:
            sbp = None
            dbp = None
        if np.random.rand() < 0.05:
            rr = None
        if np.random.rand() < 0.04:
            spo2 = None

        # 5. Conflicting Data Injection (approx 2% of cohort)
        has_conflict = False
        if spo2 is not None and spo2 >= 98.0 and np.random.rand() < 0.025:
            has_conflict = True

        # 6. Transparent Synthetic Latent Risk Score Calculation
        # Combines physiological vital deviations + demographic vulnerabilities + complaint weights + noise
        vital_penalty = 0.0
        if hr is not None:
            if hr > 110: vital_penalty += min(25.0, (hr - 110) * 0.6)
            elif hr < 50: vital_penalty += min(20.0, (50 - hr) * 0.8)
        if rr is not None:
            if rr > 22: vital_penalty += min(25.0, (rr - 22) * 1.5)
            elif rr < 10: vital_penalty += min(25.0, (10 - rr) * 2.5)
        if spo2 is not None:
            if spo2 < 95.0: vital_penalty += min(35.0, (95.0 - spo2) * 3.5)
        if sbp is not None:
            if sbp < 90: vital_penalty += min(30.0, (90 - sbp) * 1.5)
            elif sbp > 160: vital_penalty += min(20.0, (sbp - 160) * 0.5)
        if temp is not None:
            if temp > 38.5: vital_penalty += min(15.0, (temp - 38.5) * 6.0)

        pain_penalty = (pain_score or 0) * 1.5
        age_vulnerability = 8.0 if profile_choice in ["pediatric", "geriatric"] else 0.0
        noise = np.random.normal(0, 4.0)

        raw_latent_risk = 10.0 + (complaint_risk_weight * 30.0) + vital_penalty + pain_penalty + age_vulnerability + noise
        latent_risk = float(np.clip(raw_latent_risk, 0.0, 100.0))
        
        # Binary target for high acuity (1 = high/critical, 0 = moderate/low)
        high_acuity_target = 1 if latent_risk >= 50.0 else 0

        # Data completeness calculation
        present_count = sum(1 for v in [age, complaint, history_available, hr, rr, sbp, spo2, temp] if v is not None)
        completeness = round((present_count / 8.0) * 100.0, 1)

        records.append({
            "patient_id": patient_id,
            "age": age,
            "profile": profile_choice,
            "sex": sex,
            "history_available": int(history_available),
            "first_time_patient": int(first_time_patient),
            "chief_complaint": complaint,
            "symptom_duration_mins": symptom_duration,
            "pain_score": pain_score,
            "heart_rate": hr,
            "respiratory_rate": rr,
            "systolic_bp": sbp,
            "diastolic_bp": dbp,
            "spo2": spo2,
            "temperature_c": temp,
            "has_conflict": int(has_conflict),
            "data_completeness": completeness,
            "synthetic_latent_risk": round(latent_risk, 1),
            "high_acuity_target": high_acuity_target
        })

    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    os.makedirs("ml/data", exist_ok=True)
    df = generate_synthetic_cohort(2500, random_seed=42)
    output_path = "ml/data/synthetic_cohort.csv"
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} synthetic records saved to {output_path}")
    print(f"High acuity class balance: {df['high_acuity_target'].value_counts(normalize=True).to_dict()}")
