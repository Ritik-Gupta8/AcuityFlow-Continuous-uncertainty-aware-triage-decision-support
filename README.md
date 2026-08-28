<div align="center">

<img src="https://img.shields.io/badge/AcuityFlow-AI%20Triage%20Decision%20Support-0ea5e9?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiPjxwYXRoIGQ9Ik0yMiAxMmgtNGwtMyAzbC00LTgtMyA1aC00Ii8+PC9zdmc+" alt="AcuityFlow AI" />

# AcuityFlow AI

### Continuous, Uncertainty-Aware Triage Decision Support

**The emergency department never stops. Neither does AcuityFlow.**

[![Python](https://img.shields.io/badge/Python-3.13-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61dafb?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178c6?style=flat-square&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-Calibrated%20LR-f7931e?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Tests](https://img.shields.io/badge/Tests-40%20Passed-22c55e?style=flat-square&logo=pytest&logoColor=white)](./backend/tests)
[![License](https://img.shields.io/badge/License-MIT-8b5cf6?style=flat-square)](./LICENSE)

</div>

---

## 🏥 The Problem We Solve

Every minute in a busy emergency department, triage nurses face an impossible challenge:

- **Incomplete information** — a patient can't explain their history.
- **Ambiguous presentations** — chest pain could be anxiety or a STEMI.
- **Queue blindness** — a patient waiting quietly may be deteriorating.
- **Surge conditions** — 3× patient load with the same staff.

Existing triage tools give a **static score at intake, then go silent**. They don't tell you *why* they scored the patient, *how confident* that score is, or *what happened while the patient was waiting*.

**AcuityFlow AI solves all of this continuously.**

---

## 💡 What Makes AcuityFlow Different

> **The core innovation is not the initial triage score. It's the continuous, uncertainty-aware re-triage of every patient still in the waiting room.**

| Feature | Traditional Triage Tool | **AcuityFlow AI** |
|---|---|---|
| Initial risk scoring | ✅ | ✅ |
| Explains *why* it scored | ❌ | ✅ |
| Handles incomplete data | ❌ Assumes missing = normal | ✅ Escalates under uncertainty |
| Detects deterioration in queue | ❌ | ✅ (AcuityWatch Engine) |
| Handles conflicting observations | ❌ Silently resolves | ✅ ABSTAIN + Clinician flag |
| Population-specific logic | ❌ | ✅ Pediatric / Adult / Geriatric |
| Calibrated ML probability | ❌ | ✅ Calibrated Logistic Regression |
| Transparent confidence score | ❌ | ✅ 4-component uncertainty breakdown |
| Clinician override with audit log | ❌ | ✅ Immutable FHIR-style audit |
| 3× Surge mode | ❌ | ✅ |

---

## 🏗️ Architecture

```
 PATIENT ARRIVES
       │
       ▼
 ┌─────────────────┐
 │  DATA QUALITY   │  ← Completeness score, missing fields
 │     ENGINE      │
 └────────┬────────┘
          │
          ▼
 ┌─────────────────┐
 │   POPULATION    │  ← Pediatric / Adult / Geriatric resolver
 │    PROFILE      │
 └────┬────────┬───┘
      │        │
      ▼        ▼
 ┌─────────┐  ┌──────────────────────┐
 │ SAFETY  │  │  CALIBRATED ML MODEL │  ← Logistic Regression
 │  GATE   │  │  (2,500 synth cases) │     Probability Calibration
 │(AcuityG)│  └──────────┬───────────┘
 └────┬────┘             │
      │        ┌─────────▼─────────┐
      │        │  UNCERTAINTY      │  ← Model certainty
      │        │  ENGINE           │     Data reliability
      │        │                   │     Clinical consistency
      │        │                   │     Profile support
      │        └─────────┬─────────┘
      │                  │
      └──────────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │ DECISION      │  ← RECOMMEND / ESCALATE / ABSTAIN
         │ FUSION POLICY │     Safety Gate always overrides ML
         └───────┬───────┘
                 │
                 ▼
            CLINICIAN
           ┌────┴────┐
           │         │
        ACCEPT    OVERRIDE
           │         │
           └────┬────┘
                │
           AUDIT LOG
                │
                ▼
        WAITING QUEUE
                │
                ▼
          ACUITYWATCH  ← Vital deterioration detection
          (Continuous)    Overdue wait time alerts
                          Risk trajectory monitoring
                          Persistent uncertainty flags
```

---

## 🔬 ML Architecture (Honest & Transparent)

> **We don't hide what the model is. We make it debuggable.**

### Training Data
- **2,500 synthetic patient encounters** generated with fixed seed `42`
- Diverse demographics: 25% pediatric, 50% adult, 25% geriatric
- Controlled missingness: 4–15% missing rate per vital
- Transparent latent risk function — fully documented in [`docs/SYNTHETIC_DATA_GENERATION.md`](./docs/SYNTHETIC_DATA_GENERATION.md)
- **Completely independent** from the 24 acceptance test scenarios

### Model Pipeline
```
Raw Vitals + Demographics
        │
        ▼
Median Imputation + Standard Scaling + One-Hot Encoding
        │
        ▼
L2-Regularized Logistic Regression
        │
        ▼
5-Fold CalibratedClassifierCV (Sigmoid)
        │
        ▼
calibrated_model.joblib  ←  loaded at runtime
```

### Evaluation Metrics (Held-out Test Split, N=375)

| Metric | Value |
|---|---|
| **ROC-AUC** | **0.9122** |
| Accuracy | 0.8747 |
| Macro F1 | 0.7684 |
| High-Acuity Recall | 0.5139 |
| High-Acuity Precision | 0.7551 |
| **Brier Score** | **0.0850** |

> ⚠️ All metrics are computed on **synthetic demonstration data**. They do not represent real-world clinical efficacy.

### What Confidence Actually Means

```
Workflow Confidence =
    0.35 × Model Certainty        (distance from decision boundary)
  + 0.35 × Data Reliability       (intake completeness %)
  + 0.15 × Clinical Consistency   (conflict & ambiguity detection)
  + 0.15 × Profile Support        (demographic certainty)
```

**Safety Guarantee**: A lower confidence score *never* downgrades a patient's triage priority. Low confidence → `ESCALATE / CLINICIAN REVIEW`.

---

## 🛡️ Safety Gates (Non-Negotiable)

The deterministic safety layer always executes **before and after** ML inference:

| Condition | Result |
|---|---|
| SpO₂ 99% + recorded cyanosis | `ABSTAIN` — contradiction flagged |
| HR < 40 bpm or > 150 bpm (adult) | `ESCALATE` immediately |
| SpO₂ < 88% | Critical escalation |
| SBP < 90 mmHg | Shock flag |
| Uncertainty < threshold on moderate+ case | `ESCALATE` — never silently downgrade |
| Missing history with ambiguous vitals | Completeness penalty + escalation |

---

## 👁️ AcuityWatch — The Killer Feature

AcuityFlow watches every waiting patient **continuously**, not just at intake.

**Four Reassessment Triggers:**

| Trigger | Threshold |
|---|---|
| SpO₂ drop | ≥ 4% since last reading |
| Heart rate spike | ≥ 25 bpm |
| Systolic BP drop | ≥ 25 mmHg |
| Wait time overdue | Priority-window exceeded |

When triggered: creates a `REASSESSMENT RECOMMENDED` event — **never silently changing the clinician's prior decision**.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/Ritik-Gupta8/AcuityFlow-Continuous-uncertainty-aware-triage-decision-support.git
cd AcuityFlow-Continuous-uncertainty-aware-triage-decision-support
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** — the dashboard loads with 24 synthetic patients pre-seeded.

### 4. Run the Test Suite
```bash
cd backend
.venv/Scripts/pytest -v
# Expected: 40 passed in ~10s
```

### 5. (Optional) Retrain the ML Model
```bash
# From repo root
python ml/data_generation/generate_dataset.py
python ml/training/train_and_calibrate.py
python ml/evaluation/evaluate_model.py
```

---

## 🎮 Demo Walkthrough

1. **Open the Command Center** → see 24 synthetic patients in urgency order.
2. **Trigger deterioration** on PT-021 → watch SpO₂ drop to 91%, HR spike to 118. AcuityWatch flags the patient in the Attention Queue within seconds.
3. **Click a HIGH-risk patient** → inspect the full explainability card: Risk Score, Workflow Confidence, Data Completeness, Population Profile, Key Signals, Safety Flags, and Missing Information.
4. **Override** a recommendation → the system requires a structured reason. The decision is logged immutably in the Audit Trail.
5. **Toggle 3× Surge Mode** → the attention queue re-sorts, prioritizing deteriorating and overdue-reassessment patients.
6. **Open Audit Trail** → inspect the full decision history with model version, policy version, and clinician identity.

---

## 📁 Repository Structure

```
AcuityFlow-AI/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── api/                # REST endpoints
│   │   ├── core/               # Configuration & database
│   │   ├── data/               # Synthetic test case seeder (24 cases)
│   │   ├── ml/                 # Risk model, uncertainty engine, extractor
│   │   ├── models/             # SQLAlchemy ORM entities
│   │   ├── policy/             # Safety gate, completeness, decision fusion
│   │   ├── reassessment/       # AcuityWatch continuous monitor
│   │   └── schemas/            # Pydantic validation schemas
│   ├── tests/                  # 40-test pytest suite
│   └── requirements.txt
│
├── frontend/                   # React + TypeScript + Vite dashboard
│   └── src/
│       ├── components/         # Command Center, Patient Detail, Override, Audit
│       └── services/           # Backend API client
│
├── ml/                         # Offline ML training pipeline
│   ├── data_generation/        # 2,500-record synthetic cohort generator
│   ├── training/               # LR training + calibration
│   ├── evaluation/             # Model card + metrics report generator
│   └── artifacts/              # Saved .joblib model artifacts
│
└── docs/
    ├── PRODUCT_SPEC.md
    ├── TRIAGE_POLICY.md
    ├── SAFETY_UNCERTAINTY.md
    ├── DATA_SCHEMA.md
    ├── TEST_CASES.md            # 24 canonical acceptance scenarios
    ├── MODEL_CARD.md
    ├── SYNTHETIC_DATA_GENERATION.md
    ├── EVALUATION_REPORT.md
    └── FINAL_IMPLEMENTATION_REPORT.md
```

---

## 📋 Acceptance Test Coverage

All 24 canonical test scenarios from [`docs/TEST_CASES.md`](./docs/TEST_CASES.md) are verified on every push:

| Case | Scenario | Key Validation |
|---|---|---|
| PT-005 | Zero-history adult | Completeness penalty, escalation bias |
| PT-011–014 | Pediatric presentations | Profile-specific vital thresholds |
| PT-015–018 | Geriatric presentations | Age vulnerability, multi-morbidity flags |
| PT-019 | Conflicting observations | SpO₂ 99% + Cyanosis → `ABSTAIN` |
| PT-021 | Vital deterioration in queue | AcuityWatch triggers reassessment |
| PT-023–024 | Queue monitoring | Wait-time threshold detection |

---

## ⚖️ Ethical Commitments

| Principle | Implementation |
|---|---|
| **Decision Support Only** | System never autonomously acts; clinician always decides |
| **No Silent Under-Triage** | Low confidence → escalate, never downgrade |
| **Transparent Reasoning** | Every recommendation shows its full reasoning chain |
| **Clinician Authority** | Accept / Override / Escalate always available |
| **Immutable Audit** | Every decision logged with model version, policy version, timestamp |
| **Synthetic Data Only** | No real patient data used anywhere |
| **Prototype Disclaimers** | Shown persistently in the UI |

> 🚫 Not FDA cleared. Not HIPAA compliant. Not for clinical use. Production deployment requires legal, security, and clinical validation.

---

## 👥 Team

| Name | Role |
|---|---|
| Ritik Gupta | Full-Stack & ML Architecture |
| *(Teammate)* | *(Add your name & role)* |

---

## 📄 License

MIT License — see [LICENSE](./LICENSE)

---

<div align="center">

**Built with urgency. Designed with safety. Validated with honesty.**

*AcuityFlow AI — because waiting rooms shouldn't be silent risk zones.*

</div>
