# Current State of AcuityFlow Prototype

## Overview
This document records the exact state of the AcuityFlow AI repository prior to the ML training pipeline and uncertainty engine upgrade.

## 1. Triage Policy & Safety Architecture
- **Safety Gate (`backend/app/policy/safety_gate.py`)**: Authoritative deterministic checks for:
  - Critical tachycardia, bradycardia, tachypnea, bradypnea, severe hypoxia, hypertensive crisis, and hypotension.
  - Red flag symptom cues (altered mental status, lethargy, diaphoresis).
  - Observation conflict detection (e.g., SpO2 >= 98% with recorded cyanosis triggering `ABSTAIN`).
- **Population Resolver (`backend/app/policy/population.py`)**: Resolves patient age to `pediatric` (<=17), `adult` (18-64), or `geriatric` (>=65).
- **Completeness Engine (`backend/app/policy/completeness.py`)**: Computes `(available_inputs / required_inputs) * 100` and extracts missing fields (e.g. zero-history cases).
- **Action Policy (`backend/app/policy/action_policy.py`)**: Merges risk score with safety flags and conservative uncertainty thresholds, outputting `RECOMMEND`, `ESCALATE`, `REASSESS`, or `ABSTAIN`.

## 2. ML & Confidence Status (Current Starting Point)
- **Risk Model (`backend/app/ml/risk_model.py`)**: Currently implemented as a **deterministic parametric baseline** with hard-coded vital deviation weights (HR: 0.22, RR: 0.25, SpO2: 0.28, BP: 0.15, Temp: 0.10).
- **Model Artifacts**: No trained `.joblib` model is loaded at runtime.
- **Confidence**: Currently calculated via a linear completeness heuristic `(completeness * 0.7) + 25` with penalties for zero-history and ambiguous symptoms. It is **not** a calibrated ML model confidence.
- **Dataset**: No dedicated offline synthetic training dataset of 2,000+ records exists; only the 24 acceptance scenario cases in `docs/TEST_CASES.md` are defined.

## 3. Reassessment & Surge Controls
- **Reassessment Monitor (`backend/app/reassessment/monitor.py`)**: Evaluates wait times against priority windows, tracks vital deterioration deltas (SpO2 drop >=4%, HR spike >=25 bpm, SBP drop >=25 mmHg), and persistent uncertainty.
- **Surge Simulation (`backend/app/api/simulation.py`)**: Supports 3× surge mode toggle and advances ED clock (+5m, +15m).
- **Clinician Override & Audit (`backend/app/api/overrides.py`, `backend/app/api/audit.py`)**: Logs clinician overrides with mandatory reasons into a FHIR-inspired audit log.

## 4. Frontend & Testing
- **Frontend (`frontend/`)**: React + TypeScript + Vite dashboard with Command Center, Attention Queue, Patient Detail modal, Override modal, and Audit log inspector.
- **Test Suite (`backend/tests/`)**: 11 unit/integration tests currently passing.
