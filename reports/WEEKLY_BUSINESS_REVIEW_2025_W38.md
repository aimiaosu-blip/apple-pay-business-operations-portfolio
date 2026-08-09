# Digital Wallet Weekly Business Review — Week 38, 2025

> **Independent synthetic portfolio project by Aimiao Su.** This report is not affiliated with Apple Inc. or any payment provider. All issuers, transactions and findings are fictional and are used only to demonstrate an auditable business-operations workflow.

**Reporting period:** 15–21 September 2025  
**Week-over-week comparison:** 8–14 September 2025  
**Operational benchmark:** trailing four complete weeks, 18 August–14 September 2025  
**Portfolio status:** **YELLOW — stable topline with one concentrated red incident**

## Executive Summary

- **Topline volume remained stable.** Transaction attempts increased 1.1% week over week to 157,099, while synthetic GMV increased 1.2% to ¥5.44M. GMV is an illustrative payment-volume metric, not revenue.
- **Portfolio success rate softened only 0.07 percentage points versus the trailing four-week benchmark, but the aggregate masks a severe localized breach.** The affected East China / Issuer B / Transit / Older phone cut fell to 84.04%, 12.07 percentage points below baseline on 545 attempts.
- **The issue is concentrated rather than broad-based.** The rest of the portfolio remained within 0.02 percentage points of baseline. The affected cut accounts for approximately 63% of estimated excess failures versus the portfolio benchmark.
- **Immediate action is validation, not causal declaration.** Response-code mapping, route configuration and device compatibility should be tested before assigning technical cause; closure requires seven complete days within 0.5 percentage points of baseline.

## KPI Scorecard

| KPI | Current week | Prior week | Four-week benchmark | Change | Status |
|---|---:|---:|---:|---:|---|
| Transaction attempts | 157,099 | 155,341 | 154,063 weekly avg. | +1.1% WoW | GREEN |
| Successful transactions | 149,772 | 148,190 | 146,980 weekly avg. | +1.1% WoW | GREEN |
| Portfolio success rate | 95.34% | 95.40% | 95.40% | -0.07pp vs benchmark | YELLOW |
| Failed transactions | 7,327 | 7,151 | 7,083 weekly avg. | +2.5% WoW | YELLOW |
| Synthetic GMV | ¥5.44M | ¥5.38M | ¥5.34M weekly avg. | +1.2% WoW | GREEN |
| Affected-cut success rate | 84.04% | 96.53% | 96.11% | -12.07pp | RED |
| Data reconciliation errors | 0 | — | 0 tolerance | 1,680 rows checked | GREEN |

### Status contract

- **RED:** at least 500 weekly attempts and success rate at least 2.0 percentage points below the trailing four-week benchmark.
- **YELLOW:** success rate 0.5–2.0 percentage points below benchmark, or an open material incident affects an otherwise stable portfolio.
- **GREEN:** within 0.5 percentage points of benchmark with complete, reconciled data.

The benchmark is an operational reference, not a commercial target.

## The Aggregate Is Stable, but One Cut Is Not

The affected cut recorded 87 failures from 545 attempts, compared with 18 failures in the prior week. At its trailing benchmark rate, it would have produced approximately 66 fewer failures. Removing this cut leaves the rest-of-portfolio success rate at 95.38%, only 0.02 percentage points below benchmark.

This supports escalation of a bounded issuer/route/device investigation. It does **not** establish whether the mechanism is response-code mapping, token compatibility, route configuration, device software or another upstream issue.

## High-Volume Segments Below Baseline

| Segment | Attempts | Current success rate | Four-week benchmark | Delta | Status |
|---|---:|---:|---:|---:|---|
| East China / Issuer B / Transit / Older phone | 545 | 84.04% | 96.11% | -12.07pp | RED |
| South China / Issuer A / Dining / Recent phone | 711 | 94.94% | 96.34% | -1.40pp | YELLOW |
| West China / Issuer D / Retail / Watch | 615 | 93.66% | 94.91% | -1.25pp | YELLOW |
| North China / Issuer C / Dining / Older phone | 565 | 94.87% | 96.00% | -1.13pp | YELLOW |
| South China / Issuer B / Transit / Recent phone | 770 | 95.32% | 96.38% | -1.05pp | YELLOW |
| East China / Issuer D / Digital / Older phone | 632 | 94.94% | 95.90% | -0.96pp | YELLOW |

Only segments with at least 500 attempts are eligible for escalation. This volume guardrail reduces false alarms from small cuts.

## Prioritized Actions and Closure Criteria

| Priority | Action | Owner | Due | Status | Evidence required |
|---|---|---|---|---|---|
| P1 | Validate issuer response-code and route mapping for the affected cut | Payments Operations | 2025-09-16 | IN PROGRESS | Mapping review completed with evidence log |
| P2 | Reproduce the issue across issuer, transit and older-device test cases | Engineering + Issuer Partner | 2025-09-17 | IN PROGRESS | Failure pattern reproduced or ruled out |
| P3 | Prepare a bounded configuration fix and rollback decision | Product Operations | 2025-09-19 | PLANNED | Approved change and rollback criteria |
| P4 | Monitor recovery and close only after seven complete days | Business Analytics | 2025-09-28 | NOT STARTED | Success rate within 0.5pp of baseline for 7 days |

There are no carried-over actions because this is the incident-opening review. The action tracker is an illustrative operating plan; owner names refer to fictional functions rather than real teams or people.

## Further Questions

1. Did issuer response-code or route mapping change on 15 September?
2. Can the failure pattern be reproduced across device software versions and controlled transit test cases?
3. Did affected users retry successfully through another device or channel?
4. Are the lower-performing yellow segments persistent after another complete week, or random variation around baseline?

## Caveats and Assumptions

- All data are deterministic, synthetic and aggregate; no personal or payment identifiers are included.
- The dataset identifies where performance changed but does not contain governed logs or response codes needed to confirm technical root cause.
- Synthetic GMV is payment volume, not revenue or profit.
- The four-week benchmark is a monitoring reference, not a contractual target.
- Calendar dates are synthetic daily aggregates; no intraday timezone conversion is required.
- Funnel and 30-day repeat metrics are maintained elsewhere in the portfolio and are intentionally excluded from this incident-opening scorecard because the relevant cohorts are not mature at the reporting cutoff.

## Reproducibility

Run the following after generating the synthetic SQLite database:

```bash
python scripts/generate_weekly_review.py
python scripts/build_weekly_review_artifacts.py
```

The report is generated from `data/apple_pay_operations.sqlite` using fixed seed `20260810`. Supporting evidence is saved in `data/processed/weekly_business_review_2025_w38.json`.
