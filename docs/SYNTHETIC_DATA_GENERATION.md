# Synthetic Data Generation Methodology

## 1. Important Prototype Disclaimer
> **Labels are synthetic demonstration labels and are NOT clinical outcomes.**
> This synthetic dataset is constructed solely to develop, train, evaluate, and demonstrate an ML pipeline and probability calibration architecture. It does not represent actual clinical prevalence, patient records, or medical truth.

## 2. Cohort Structure & Parameters
- **Size**: 2,500 synthetic patient encounters.
- **Random Seed**: Fixed at `42` for exact reproducibility.
- **Demographic Split**:
  - **Pediatric (25%)**: Ages 1–17. Baseline vitals parameterized for pediatric norms (higher baseline HR/RR, lower SBP).
  - **Adult (50%)**: Ages 18–64. Baseline vitals parameterized for adult norms.
  - **Geriatric (25%)**: Ages 65–95. Higher baseline SBP, lower HR, increased vulnerability.
- **History Availability**:
  - Full history available: 60%
  - Partial history available: 25%
  - Zero-history / First-time presentation: 15%

## 3. Controlled Missingness & Noise
- Real-world triage data features incomplete observations. The generator introduces controlled missing values:
  - Missing body temperature: ~8% of records
  - Missing blood pressure (systolic/diastolic): ~6% of records
  - Missing respiratory rate: ~5% of records
  - Missing SpO2: ~4% of records
  - Missing pain score: ~15% of records
- Gaussian noise ($\sigma = 4.0$) is added to latent physiological risk calculations.

## 4. Synthetic Latent Risk Function
The latent risk score (0–100) is generated via a transparent multi-factor function:
$$\text{Latent Risk} = 10.0 + (w_{\text{complaint}} \times 30) + \text{Vital Penalties} + (\text{Pain} \times 1.5) + \text{Age Vulnerability} + \epsilon$$

Where:
- $\text{Vital Penalties}$ penalize severe deviations in HR (>110 or <50), RR (>22 or <10), SpO2 (<95%), SBP (<90 or >160), and Temp (>38.5°C).
- $\text{Age Vulnerability}$ adds +8.0 pts for pediatric and geriatric cases.
- $\epsilon \sim \mathcal{N}(0, 4.0)$ provides stochastic variation.
- The binary classification target `high_acuity_target` is defined as $\mathbb{I}(\text{Latent Risk} \ge 50.0)$.

## 5. Separation from Acceptance Tests
This dataset is **strictly independent** from the 24 acceptance scenarios in `docs/TEST_CASES.md`. The ML model is trained only on this synthetic cohort and evaluated on held-out test splits.
