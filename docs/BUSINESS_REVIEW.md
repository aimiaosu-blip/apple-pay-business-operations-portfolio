# Weekly / Monthly Business Review Framework

## Completed recruiter-facing example

- **[Open the complete Week 38 review](https://aimiaosu-blip.github.io/apple-pay-business-operations-portfolio/reports/weekly-business-review-week-38.html)**
- [Read the Markdown report](../reports/WEEKLY_BUSINESS_REVIEW_2025_W38.md)
- [Inspect the reviewed evidence](../data/processed/weekly_business_review_2025_w38.json)
- [Review the basic-Python generator](../scripts/generate_weekly_review.py)

The completed report covers 15–21 September 2025, compares the period with the prior complete week and a trailing four-week weighted benchmark, assigns explicit red/yellow/green status, isolates a volume-qualified incident, and translates the finding into owner-based actions and closure criteria.

## Executive summary

The synthetic portfolio grows through 2025 while aggregate success rate remains high. A deliberately planted, bounded incident from 15 September to 5 October produces a visible localized dip. The completed Week 38 review identifies East China / Issuer B / Transit / Older phone as the only high-volume red breach rather than treating the event as a portfolio-wide demand shift.

## Review cadence

1. KPI scorecard: attempts, success rate, failure rate and synthetic GMV.
2. Comparison: prior complete week and trailing four complete weeks.
3. Reliability cuts: region, issuer, category and device.
4. Exceptions: threshold breaches and data-quality tests.
5. Action tracker: priority, owner, due date, validation metric and status.
6. Closure review: seven complete days within 0.5 percentage points of baseline.

## Decision rule

Escalate when a segment with at least 500 weekly attempts is at least 2 percentage points below its trailing four-week weighted baseline. Validate denominator stability and upstream data completeness before assigning operational cause.

The four-week baseline is a monitoring reference, not a commercial target. All data, owners and findings are synthetic and illustrative.
