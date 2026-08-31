# AcuityFlow AI

### Continuous, uncertainty-aware emergency-department triage decision support.

AcuityFlow AI helps emergency-department staff:
- **structure patient intake**,
- **estimate risk** with calibrated probabilistic scoring,
- **surface uncertainty** and missing clinical data,
- **prioritize clinician attention** on high-acuity cases,
- **monitor waiting patients for deterioration** over time,
- **support reassessment** with proactive alerts,
- **preserve clinician authority** with structured overrides, and
- **maintain an auditable decision history** across all interactions.

[![Python](https://img.shields.io/badge/Python-3.13-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61dafb?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8-3178c6?style=flat-square&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-Calibrated%20LR-f7931e?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Tests](https://img.shields.io/badge/Tests-75%20Passed-22c55e?style=flat-square&logo=pytest&logoColor=white)](./backend/tests)
[![License](https://img.shields.io/badge/License-MIT-8b5cf6?style=flat-square)](./LICENSE)

---

## Overview

Traditional emergency department triage assigns a static acuity score at intake, and then goes silent. However, clinical state in the waiting room is dynamic: patients can deteriorate, information may arrive late, and initial observations can be incomplete or conflicting.

**AcuityFlow AI** provides continuous, uncertainty-aware decision support from initial walk-in through ongoing waiting-room reassessment. It combines deterministic clinical safety gates, population-specific calibration, a multi-factor uncertainty engine, and continuous re-triage monitoring to assist clinical staff without ever usurping human clinical authority.

---

## Why AcuityFlow

- **Initial triage is only a snapshot**: A vital sign recorded at 08:00 AM may not reflect patient acuity at 09:30 AM.
- **Patient state changes while waiting**: Subtle changes in heart rate, SpO₂, or blood pressure can signal early decompensation.
- **Information is often incomplete or conflicting**: Zero-history arrivals, missing vitals, or contradictory observations (e.g., normal SpO₂ with cyanosis) require cautious safety defaults rather than naive guesses.
- **Clinicians retain ultimate authority**: AI provides structured decision support; clinicians decide, accept, escalate, or override.

---

## Core Product Principle

> **AI recommends. Clinicians decide. The system never stops watching.**

---

## Core Innovation

### Continuous Risk-Aware Re-Triage

The central capability of AcuityFlow is **continuous waiting-room monitoring (AcuityWatch)**. The system tracks dynamic vitals, elapsed wait times, and trajectory deltas for all patients in queue:

```text
Patient Intake
      ↓
Initial Assessment & Recommendation
      ↓
Waiting Queue (Continuous Monitoring)
      ↓
New Observations / Time Progression
      ↓
Risk Trajectory Delta (AcuityWatch Engine)
      ↓
Reassessment Recommendation Alert
      ↓
Clinician Review & Decision
```

#### Key Monitoring Triggers:
1. **Vital Deterioration**: SpO₂ drop ≥ 4%, Heart Rate spike ≥ 25 bpm, Systolic BP drop ≥ 25 mmHg.
2. **Overdue Waiting Windows**: Time elapsed exceeding urgency policy boundaries (e.g., HIGH acuity waiting > 30m).
3. **Surge Adaptation**: Under 3× surge load, the attention queue prioritizes deteriorating and overdue patients without modifying medical thresholds.

---

## How It Works

```text
Patient Intake
      ↓
Data Quality (Completeness & Missing Fields)
      ↓
Population Profile (Pediatric / Adult / Geriatric)
      ↓
Safety Gate (Deterministic Critical Vitals & Conflict Checks)
      ↓
Calibrated Risk Model (Scikit-Learn Logistic Regression)
      ↓
Uncertainty Engine (Model, Data, Consistency, Profile)
      ↓
Decision Policy (RECOMMEND / ESCALATE / ABSTAIN)
      ↓
Clinician Review (Accept / Override with Mandatory Reason)
      ↓
Audit Trail (Immutable JWT-Verified Session Log)
      ↓
Waiting Queue
      ↓
AcuityWatch (Continuous Trajectory & Wait-Time Monitor)
      ↓
Reassessment
```

---

## Architecture & Subsystems

### 1. Multi-Factor Uncertainty Engine
AcuityFlow explicitly surfaces workflow confidence alongside risk scores:
$$\text{Workflow Confidence} = 0.35 \times \text{Model Certainty} + 0.35 \times \text{Data Reliability} + 0.15 \times \text{Clinical Consistency} + 0.15 \times \text{Profile Support}$$

- **Escalation-Bias Invariant**: When confidence drops or data is missing, the system **escalates to clinical review**—it *never* silently downgrades priority.

### 2. Deterministic Safety Gates
Hard safety boundaries always take precedence over statistical model predictions:
- Critical vitals (e.g., adult HR > 150 bpm, SpO₂ < 88%, SBP < 90 mmHg) trigger immediate `ESCALATE`.
- Contradictory inputs (e.g., SpO₂ ≥ 98% with recorded cyanosis) trigger `ABSTAIN / CLINICIAN REVIEW`.

### 3. Population-Specific Policies
Every patient resolves to a distinct population profile with customized normal ranges and scoring policies:
- **Pediatric** (Age ≤ 17)
- **Adult** (Age 18–64)
- **Geriatric** (Age ≥ 65)

### 4. Backend-Enforced Role-Based Access Control (RBAC)
- **Authentication**: Cryptographically salted PBKDF2-HMAC-SHA256 password hashing with HS256 JWT access tokens.
- **Role Permissions**:
  - **Nurse** (`nurse101`): Frontline queue, vital entry, triage evaluation, clinical overrides, patient audit.
  - **Supervisor** (`supervisor101`): All nurse capabilities + system-wide audit trail explorer and override review.
  - **Admin** (`admin101`): Demographic policy configuration & user management.
- **Spoofing Prevention**: Clinician identity on overrides is authoritatively derived from the verified token signature.

---

## Machine Learning & Evaluation

- **Synthetic Cohort**: 2,500 patient encounters generated with fixed seed `42` (`ml/data/synthetic_cohort.csv`), strictly independent from the 24 acceptance scenarios.
- **Model Pipeline**: Preprocessing (median imputation + standard scaling + one-hot encoding) + L2 Logistic Regression + 5-fold Sigmoid Calibration (`CalibratedClassifierCV`).
- **Performance on Held-Out Test Set (N=375)**:
  - **ROC-AUC**: **0.9122**
  - **Brier Score**: **0.0850** (Calibrated probability accuracy)
  - **Accuracy**: 0.8747
  - **Macro F1**: 0.7684

*All metrics reflect synthetic demonstration data and do not represent real-world clinical validation.*

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Clone & Setup Backend
```bash
# Clone repository
git clone https://github.com/Ritik-Gupta8/AcuityFlow-Continuous-uncertainty-aware-triage-decision-support.git
cd AcuityFlow-Continuous-uncertainty-aware-triage-decision-support

# Backend environment setup
cd backend
python -m venv .venv

# Activate environment (Windows)
.venv\Scripts\activate
# Activate environment (macOS/Linux)
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Setup Frontend
```bash
cd ../frontend
npm install
npm run dev
```

### 3. Open Application
Navigate to **http://localhost:5173/**:
- Sign in with any pre-configured demo account:
  - **Nurse**: `nurse101` / `Password@123`
  - **Supervisor**: `supervisor101` / `Password@123`
  - **Admin**: `admin101` / `Password@123`

### 4. Run Test Suite
```bash
cd backend
.venv/Scripts/pytest -v
# 75 passed across unit, policy, reassessment, ML, and RBAC security tests
```

---

## Project Structure

```
AcuityFlow/
├── backend/
│   ├── app/
│   │   ├── api/             # REST API endpoints (auth, patients, audit, admin, simulation)
│   │   ├── core/            # Config, database, security, password hashing, JWT
│   │   ├── data/            # 24 canonical synthetic test cases & seeder
│   │   ├── ml/              # Risk model runtime loader & uncertainty engine
│   │   ├── models/          # SQLAlchemy database entities
│   │   ├── policy/          # Safety gate, population resolver, completeness, decision fusion
│   │   ├── reassessment/    # AcuityWatch waiting-room monitor
│   │   └── schemas/         # Pydantic validation schemas
│   ├── tests/               # 75-test pytest suite (RBAC, safety, policy, ML)
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/      # LoginPage, CommandCenter, PatientDetail, Override, Audit, Admin
│   │   ├── services/        # Authenticated API client
│   │   └── types.ts         # TypeScript domain models
│   └── index.html
│
├── ml/
│   ├── data_generation/     # 2,500 synthetic cohort generator
│   ├── training/            # Logistic regression training & calibration scripts
│   ├── evaluation/          # Model evaluation & metrics reporting
│   └── artifacts/           # Saved .joblib model artifacts
│
└── docs/                    # Architectural specifications & reports
    ├── PRODUCT_SPEC.md
    ├── TRIAGE_POLICY.md
    ├── SAFETY_UNCERTAINTY.md
    ├── DATA_SCHEMA.md
    ├── TEST_CASES.md
    ├── PRIVACY_SECURITY.md
    ├── RBAC_IMPLEMENTATION_REPORT.md
    └── EVALUATION_REPORT.md
```

---

## Prototype Disclaimers & Ethics

- **Decision Support Only**: AcuityFlow AI provides priority recommendations and risk signals; it does not formulate diagnoses or prescribe medical treatment.
- **Clinician Accountability**: All clinical actions remain under human clinical authority. Clinicians can accept, override, or escalate recommendations at any time.
- **Synthetic Data**: All patient profiles, vital observations, and scenarios are synthetically generated. No real patient health information (PHI) is used.
- **Regulatory Status**: This is an educational research prototype. It is **not** FDA/MDR cleared, **not** HIPAA/DPDP certified, and **not** approved for clinical use.

---

## License

MIT License — see [LICENSE](./LICENSE)
