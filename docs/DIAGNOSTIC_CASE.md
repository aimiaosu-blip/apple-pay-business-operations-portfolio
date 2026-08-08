# Diagnostic Case: A Concentrated Success-Rate Drop

## Symptom
The synthetic aggregate success rate dips during 15 Sep–5 Oct 2025.

## Method
Recompute numerator and denominator; confirm transaction balance; compare equal windows; rank region × issuer × category × device cuts by success rate with minimum-volume guardrail; compare the lowest cut with its preceding baseline.

## Finding
The issue is intentionally concentrated in **East China / Issuer B / Transit / Older phone**. Other segments remain near their generated baselines. This is a portfolio dataset finding, not a claim about Apple or any issuer.

## Hypotheses to test in a real operation
Issuer response-code mapping; token/provisioning compatibility; route configuration; device OS/version interaction; merchant terminal changes. The synthetic data cannot distinguish these mechanisms.

## Recommendation
Open a joint issuer/engineering investigation, validate logs in a privacy-safe environment, define a rollback decision, and monitor 7-day success-rate recovery with volume and data-completeness guardrails.
