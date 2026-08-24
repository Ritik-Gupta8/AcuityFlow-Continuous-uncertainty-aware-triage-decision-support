# Round 2 Submission Checklist

## Functional

- [ ] 20+ synthetic patient records
- [ ] ambiguous presentation
- [ ] pediatric case
- [ ] geriatric case
- [ ] zero-history case
- [ ] explicit confidence
- [ ] explicit uncertainty
- [ ] escalation-biased behavior
- [ ] waiting-queue monitoring
- [ ] deterioration-triggered reassessment
- [ ] 3× surge mode
- [ ] clinician override
- [ ] override reason logged
- [ ] audit trail visible
- [ ] hospital configuration concept

## Safety

- [ ] no diagnosis claim
- [ ] no treatment recommendation
- [ ] no autonomous clinical decision
- [ ] synthetic-data disclaimer
- [ ] missing data is not treated as negative
- [ ] conflicting data is surfaced
- [ ] low confidence does not silently downgrade risk
- [ ] every recommendation explains why
- [ ] model/policy version visible in logs

## Engineering

- [ ] backend validation
- [ ] unit tests
- [ ] policy tests
- [ ] surge test
- [ ] re-triage test
- [ ] override test
- [ ] authorization test
- [ ] audit test
- [ ] README
- [ ] architecture diagram
- [ ] setup instructions
- [ ] deployment instructions

## AI

- [ ] Gemini use is bounded
- [ ] Gemini fallback exists
- [ ] no direct LLM-to-triage authority
- [ ] structured output validation
- [ ] prompt version recorded where relevant

## Cloud

- [ ] billing budget created
- [ ] service max instances configured
- [ ] minimum instances zero unless needed
- [ ] no idle expensive resources
- [ ] credits usage reviewed
- [ ] deployed demo URL tested

## Video

- [ ] actual working prototype shown
- [ ] concept/prototype disclaimer
- [ ] ambiguous case
- [ ] pediatric/geriatric case
- [ ] zero-history case
- [ ] surge mode
- [ ] deterioration
- [ ] override
- [ ] audit trail
- [ ] strong closing message
