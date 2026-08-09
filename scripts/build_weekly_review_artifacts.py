"""Render the reviewed KPI snapshot into recruiter-facing report artifacts."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data/processed/weekly_business_review_2025_w38.json"
REPORT_DIR = ROOT / "reports"
MARKDOWN_PATH = REPORT_DIR / "WEEKLY_BUSINESS_REVIEW_2025_W38.md"
ARTIFACT_PATH = REPORT_DIR / "weekly_business_review_2025_w38_artifact.json"


def pct(value):
    return f"{value * 100:.2f}%"


def pp(value):
    return f"{value:+.2f}pp"


def compact_number(value):
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}k"
    return f"{value:,.0f}"


def build_markdown(data):
    current = data["current"]
    prior = data["prior"]
    baseline = data["baseline_4w"]
    changes = data["changes"]
    affected = data["affected_segment"]
    rest = data["rest_of_portfolio"]
    quality = data["data_quality"]

    total_excess_failures = (
        current["attempts"] * baseline["success_rate"]
        - current["successful_transactions"]
    )
    affected_share = (
        affected["estimated_excess_failures_vs_baseline"] / total_excess_failures
        if total_excess_failures > 0
        else 0
    )

    segment_rows = []
    for row in data["lowest_segments"][:6]:
        segment_rows.append(
            f"| {row['segment']} | {row['attempts']:,} | "
            f"{pct(row['success_rate'])} | {pct(row['baseline_success_rate'])} | "
            f"{pp(row['delta_pp'])} | {row['status']} |"
        )

    action_rows = []
    for row in data["action_tracker"]:
        action_rows.append(
            f"| P{row['priority']} | {row['action']} | {row['owner']} | "
            f"{row['due_date']} | {row['status']} | {row['validation_metric']} |"
        )

    return f"""# Digital Wallet Weekly Business Review — Week 38, 2025

> **Independent synthetic portfolio project by Aimiao Su.** This report is not affiliated with Apple Inc. or any payment provider. All issuers, transactions and findings are fictional and are used only to demonstrate an auditable business-operations workflow.

**Reporting period:** 15–21 September 2025  
**Week-over-week comparison:** 8–14 September 2025  
**Operational benchmark:** trailing four complete weeks, 18 August–14 September 2025  
**Portfolio status:** **YELLOW — stable topline with one concentrated red incident**

## Executive Summary

- **Topline volume remained stable.** Transaction attempts increased {changes['attempts_vs_prior']['relative'] * 100:.1f}% week over week to {current['attempts']:,}, while synthetic GMV increased {changes['gmv_vs_prior']['relative'] * 100:.1f}% to ¥{compact_number(current['gmv_cny'])}. GMV is an illustrative payment-volume metric, not revenue.
- **Portfolio success rate softened only {abs(changes['success_rate_vs_baseline']['absolute'] * 100):.2f} percentage points versus the trailing four-week benchmark, but the aggregate masks a severe localized breach.** The affected East China / Issuer B / Transit / Older phone cut fell to {pct(affected['current']['success_rate'])}, {abs(affected['delta_vs_baseline_pp']):.2f} percentage points below baseline on {affected['current']['attempts']:,} attempts.
- **The issue is concentrated rather than broad-based.** The rest of the portfolio remained within {abs(rest['delta_vs_baseline_pp']):.2f} percentage points of baseline. The affected cut accounts for approximately {affected_share * 100:.0f}% of estimated excess failures versus the portfolio benchmark.
- **Immediate action is validation, not causal declaration.** Response-code mapping, route configuration and device compatibility should be tested before assigning technical cause; closure requires seven complete days within 0.5 percentage points of baseline.

## KPI Scorecard

| KPI | Current week | Prior week | Four-week benchmark | Change | Status |
|---|---:|---:|---:|---:|---|
| Transaction attempts | {current['attempts']:,} | {prior['attempts']:,} | {baseline['attempts'] / 4:,.0f} weekly avg. | {changes['attempts_vs_prior']['relative'] * 100:+.1f}% WoW | GREEN |
| Successful transactions | {current['successful_transactions']:,} | {prior['successful_transactions']:,} | {baseline['successful_transactions'] / 4:,.0f} weekly avg. | {(current['successful_transactions'] / prior['successful_transactions'] - 1) * 100:+.1f}% WoW | GREEN |
| Portfolio success rate | {pct(current['success_rate'])} | {pct(prior['success_rate'])} | {pct(baseline['success_rate'])} | {pp(changes['success_rate_vs_baseline']['absolute'] * 100)} vs benchmark | YELLOW |
| Failed transactions | {current['failed_transactions']:,} | {prior['failed_transactions']:,} | {baseline['failed_transactions'] / 4:,.0f} weekly avg. | {changes['failed_vs_prior']['relative'] * 100:+.1f}% WoW | YELLOW |
| Synthetic GMV | ¥{compact_number(current['gmv_cny'])} | ¥{compact_number(prior['gmv_cny'])} | ¥{compact_number(baseline['gmv_cny'] / 4)} weekly avg. | {changes['gmv_vs_prior']['relative'] * 100:+.1f}% WoW | GREEN |
| Affected-cut success rate | {pct(affected['current']['success_rate'])} | {pct(affected['prior']['success_rate'])} | {pct(affected['baseline_4w']['success_rate'])} | {pp(affected['delta_vs_baseline_pp'])} | RED |
| Data reconciliation errors | {quality['transaction_balance_errors']} | — | 0 tolerance | {quality['rows_in_report_week']:,} rows checked | GREEN |

### Status contract

- **RED:** at least 500 weekly attempts and success rate at least 2.0 percentage points below the trailing four-week benchmark.
- **YELLOW:** success rate 0.5–2.0 percentage points below benchmark, or an open material incident affects an otherwise stable portfolio.
- **GREEN:** within 0.5 percentage points of benchmark with complete, reconciled data.

The benchmark is an operational reference, not a commercial target.

## The Aggregate Is Stable, but One Cut Is Not

The affected cut recorded {affected['current']['failed_transactions']} failures from {affected['current']['attempts']} attempts, compared with {affected['prior']['failed_transactions']} failures in the prior week. At its trailing benchmark rate, it would have produced approximately {affected['estimated_excess_failures_vs_baseline']:.0f} fewer failures. Removing this cut leaves the rest-of-portfolio success rate at {pct(rest['current']['success_rate'])}, only {abs(rest['delta_vs_baseline_pp']):.2f} percentage points below benchmark.

This supports escalation of a bounded issuer/route/device investigation. It does **not** establish whether the mechanism is response-code mapping, token compatibility, route configuration, device software or another upstream issue.

## High-Volume Segments Below Baseline

| Segment | Attempts | Current success rate | Four-week benchmark | Delta | Status |
|---|---:|---:|---:|---:|---|
{chr(10).join(segment_rows)}

Only segments with at least 500 attempts are eligible for escalation. This volume guardrail reduces false alarms from small cuts.

## Prioritized Actions and Closure Criteria

| Priority | Action | Owner | Due | Status | Evidence required |
|---|---|---|---|---|---|
{chr(10).join(action_rows)}

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
"""


def build_artifact(data):
    current = data["current"]
    prior = data["prior"]
    baseline = data["baseline_4w"]
    affected = data["affected_segment"]
    rest = data["rest_of_portfolio"]
    changes = data["changes"]
    quality = data["data_quality"]

    total_excess_failures = (
        current["attempts"] * baseline["success_rate"]
        - current["successful_transactions"]
    )
    affected_share = (
        affected["estimated_excess_failures_vs_baseline"] / total_excess_failures
        if total_excess_failures > 0
        else 0
    )

    kpi_summary = [
        {
            "success_rate": current["success_rate"],
            "success_rate_prior": prior["success_rate"],
            "success_rate_delta_pp": changes["success_rate_vs_baseline"]["absolute"]
            * 100,
            "attempts": current["attempts"],
            "attempts_wow": changes["attempts_vs_prior"]["relative"],
            "gmv_cny": current["gmv_cny"],
            "gmv_wow": changes["gmv_vs_prior"]["relative"],
            "affected_success_rate": affected["current"]["success_rate"],
            "affected_delta_pp": affected["delta_vs_baseline_pp"],
            "quality_errors": quality["transaction_balance_errors"],
            "rows_checked": quality["rows_in_report_week"],
        }
    ]

    segment_rows = [
        {
            "segment": row["segment"],
            "attempts": row["attempts"],
            "current_success_rate": row["success_rate"],
            "baseline_success_rate": row["baseline_success_rate"],
            "delta_pp": row["delta_pp"],
            "status": row["status"],
        }
        for row in data["lowest_segments"][:6]
    ]

    source = {
        "id": "synthetic-weekly-review",
        "label": "Deterministic synthetic digital-wallet operations review",
        "path": "data/processed/weekly_business_review_2025_w38.json",
        "query": {
            "language": "sql",
            "engine": "SQLite",
            "description": "Reproduces the Week 38 portfolio KPIs, trailing benchmark, segment diagnostic and quality checks from aggregate synthetic data.",
            "executed_at": "2026-08-09T00:00:00+08:00",
            "sql": "SELECT date, region, issuer, merchant_category, device_segment, attempts, successful_transactions, failed_transactions, gmv_cny, is_anomaly_window, is_synthetic FROM fact_daily_operations WHERE date BETWEEN '2025-08-18' AND '2025-09-21' ORDER BY date, region, issuer, merchant_category, device_segment;",
            "tables_used": [
                "data/apple_pay_operations.sqlite.fact_daily_operations"
            ],
            "filters": [
                "Report week: 2025-09-15 through 2025-09-21",
                "Prior week: 2025-09-08 through 2025-09-14",
                "Trailing baseline: 2025-08-18 through 2025-09-14",
                "Escalation rows require at least 500 weekly attempts",
            ],
            "metric_definitions": [
                "Success rate = summed successful transactions / summed attempts",
                "Percentage-point delta = current success rate minus trailing four-week weighted success rate",
                "GMV is synthetic successful payment volume and is not revenue",
            ],
        },
    }

    action_source = {
        "id": "illustrative-action-plan",
        "label": "Illustrative owner-based incident action plan",
        "path": "scripts/build_weekly_review_artifacts.py",
        "query": {
            "language": "sql",
            "engine": "SQLite",
            "description": "Fictional owner, timing, status and validation fields created for the synthetic incident response.",
            "executed_at": "2026-08-09T00:00:00+08:00",
            "sql": "WITH actions(priority, action, owner, due_date, status, validation_metric) AS (VALUES (1, 'Validate issuer response-code and route mapping for the affected cut', 'Payments Operations', '2025-09-16', 'IN PROGRESS', 'Mapping review completed with evidence log'), (2, 'Reproduce the issue across issuer, transit and older-device test cases', 'Engineering + Issuer Partner', '2025-09-17', 'IN PROGRESS', 'Failure pattern reproduced or ruled out'), (3, 'Prepare a bounded configuration fix and rollback decision', 'Product Operations', '2025-09-19', 'PLANNED', 'Approved change and rollback criteria'), (4, 'Monitor recovery and close only after seven complete days', 'Business Analytics', '2025-09-28', 'NOT STARTED', 'Success rate within 0.5pp of baseline for 7 days')) SELECT * FROM actions ORDER BY priority;",
        },
    }

    executive_summary = f"""## Executive Summary

- **Portfolio status is YELLOW.** Attempts increased {changes['attempts_vs_prior']['relative'] * 100:.1f}% week over week and synthetic GMV increased {changes['gmv_vs_prior']['relative'] * 100:.1f}%, while weighted success rate declined only {abs(changes['success_rate_vs_baseline']['absolute'] * 100):.2f} percentage points versus the trailing benchmark.
- **One high-volume cut is RED.** East China / Issuer B / Transit / Older phone fell to {pct(affected['current']['success_rate'])}, {abs(affected['delta_vs_baseline_pp']):.2f} percentage points below baseline on {affected['current']['attempts']:,} attempts.
- **The incident is concentrated.** The rest of the portfolio remained within {abs(rest['delta_vs_baseline_pp']):.2f} percentage points of baseline; the affected cut explains approximately {affected_share * 100:.0f}% of estimated excess failures.
- **Validate before assigning cause.** Response-code mapping, routing and device compatibility require controlled testing; closure needs seven complete days within 0.5 percentage points of baseline.
"""

    artifact = {
        "surface": "report",
        "manifest": {
            "version": 1,
            "surface": "report",
            "title": "Digital Wallet Weekly Business Review — Week 38, 2025",
            "description": "A recruiter-facing synthetic operations review with KPI status, segment diagnosis, actions and closure criteria.",
            "generatedAt": "2026-08-09T00:00:00+08:00",
            "sources": [source, action_source],
            "cards": [
                {
                    "id": "card-success-rate",
                    "description": "Weighted successful transactions divided by attempts for 15–21 September 2025.",
                    "dataset": "kpi_summary",
                    "sourceId": "synthetic-weekly-review",
                    "metrics": [
                        {"label": "Portfolio success rate · YELLOW", "field": "success_rate", "format": "percent"},
                        {"label": "Prior", "field": "success_rate_prior", "format": "percent"},
                        {"label": "vs benchmark", "field": "success_rate_delta_pp", "format": "number", "signed": True},
                    ],
                },
                {
                    "id": "card-attempts",
                    "description": "All aggregate transaction attempts in the complete seven-day report week.",
                    "dataset": "kpi_summary",
                    "sourceId": "synthetic-weekly-review",
                    "metrics": [
                        {"label": "Transaction attempts · GREEN", "field": "attempts", "format": "number"},
                        {"label": "WoW", "field": "attempts_wow", "format": "percent", "signed": True},
                    ],
                },
                {
                    "id": "card-gmv",
                    "description": "Successful payment volume in CNY; this is not revenue.",
                    "dataset": "kpi_summary",
                    "sourceId": "synthetic-weekly-review",
                    "metrics": [
                        {"label": "Synthetic GMV · GREEN", "field": "gmv_cny", "format": "currency", "unit": "CNY"},
                        {"label": "WoW", "field": "gmv_wow", "format": "percent", "signed": True},
                    ],
                },
                {
                    "id": "card-affected",
                    "description": "East China / Issuer B / Transit / Older phone; 545 weekly attempts.",
                    "dataset": "kpi_summary",
                    "sourceId": "synthetic-weekly-review",
                    "metrics": [
                        {"label": "Affected-cut success rate · RED", "field": "affected_success_rate", "format": "percent"},
                        {"label": "vs benchmark", "field": "affected_delta_pp", "format": "number", "signed": True},
                    ],
                },
                {
                    "id": "card-quality",
                    "description": "Attempt balance and synthetic-data flags checked across the report week.",
                    "dataset": "kpi_summary",
                    "sourceId": "synthetic-weekly-review",
                    "metrics": [
                        {"label": "Data reconciliation errors · GREEN", "field": "quality_errors", "format": "number"},
                        {"label": "Rows checked", "field": "rows_checked", "format": "number"},
                    ],
                },
            ],
            "charts": [
                {
                    "id": "chart-diagnostic-trend",
                    "title": "Daily transaction success rate",
                    "description": "Trailing four-week baseline plus Week 38; affected segment compared with the rest of the portfolio.",
                    "type": "line",
                    "dataset": "diagnostic_daily",
                    "sourceId": "synthetic-weekly-review",
                    "encodings": {
                        "x": {"field": "date", "type": "temporal", "title": "Date"},
                        "y": {"field": "success_rate", "type": "quantitative", "title": "Success rate", "format": "percent"},
                        "color": {"field": "series", "type": "nominal", "title": "Portfolio cut"},
                    },
                }
            ],
            "tables": [
                {
                    "id": "table-segments",
                    "title": "High-volume segment performance",
                    "description": "Only cuts with at least 500 Week 38 attempts; ordered by percentage-point movement versus the trailing benchmark.",
                    "dataset": "segment_rows",
                    "sourceId": "synthetic-weekly-review",
                    "columns": [
                        {"field": "segment", "label": "Segment", "type": "text"},
                        {"field": "attempts", "label": "Attempts", "type": "number"},
                        {"field": "current_success_rate", "label": "Current", "type": "percent"},
                        {"field": "baseline_success_rate", "label": "Benchmark", "type": "percent"},
                        {"field": "delta_pp", "label": "Delta (pp)", "type": "number", "semantic": "movement"},
                        {"field": "status", "label": "Status", "type": "text"},
                    ],
                    "defaultSort": {"field": "delta_pp", "direction": "asc"},
                },
                {
                    "id": "table-actions",
                    "title": "Incident action tracker",
                    "description": "Illustrative owners, deadlines, progress and evidence required for closure.",
                    "dataset": "action_rows",
                    "sourceId": "illustrative-action-plan",
                    "columns": [
                        {"field": "priority", "label": "Priority", "type": "number"},
                        {"field": "action", "label": "Action", "type": "text"},
                        {"field": "owner", "label": "Owner", "type": "text"},
                        {"field": "due_date", "label": "Due", "type": "date"},
                        {"field": "status", "label": "Status", "type": "text"},
                        {"field": "validation_metric", "label": "Evidence required", "type": "text"},
                    ],
                    "defaultSort": {"field": "priority", "direction": "asc"},
                },
            ],
            "blocks": [
                {"id": "title", "type": "markdown", "body": "# Digital Wallet Weekly Business Review — Week 38, 2025"},
                {"id": "executive-summary", "type": "markdown", "body": executive_summary, "sourceId": "synthetic-weekly-review"},
                {"id": "kpi-strip", "type": "metric-strip", "cardIds": ["card-success-rate", "card-attempts", "card-gmv", "card-affected", "card-quality"]},
                {"id": "status-contract", "type": "markdown", "body": "## How to Read the Status\n\n**RED** requires at least 500 weekly attempts and a success rate at least 2.0 percentage points below the trailing four-week benchmark. **YELLOW** marks a 0.5–2.0 point decline or an open material incident. **GREEN** means performance remains within 0.5 points with complete reconciled data. The benchmark is an operational reference, not a commercial target."},
                {"id": "finding-concentration", "type": "markdown", "body": f"## One Cut Drives the Material Risk\n\nThe affected cut fell to **{pct(affected['current']['success_rate'])}**, while the rest of the portfolio stayed at **{pct(rest['current']['success_rate'])}**. The chart shows the affected cut breaking sharply from its prior range on 15 September; the portfolio remainder stays stable. This supports a bounded investigation, not a confirmed technical cause.", "sourceId": "synthetic-weekly-review"},
                {"id": "diagnostic-chart", "type": "chart", "chartId": "chart-diagnostic-trend"},
                {"id": "segment-finding", "type": "markdown", "body": "## Only One High-Volume Cut Breaches the Red Threshold\n\nThe ranked table applies the same 500-attempt guardrail to every segment. Smaller or moderate movements remain yellow or green; the East China / Issuer B / Transit / Older phone cut is the only red breach. This concentration protects the team from treating portfolio-wide demand as the problem."},
                {"id": "segment-table", "type": "table", "tableId": "table-segments"},
                {"id": "actions-heading", "type": "markdown", "body": "## Prioritized Actions and Closure Criteria\n\nValidate response-code mapping and reproduce the issue before changing configuration. Any change needs an explicit rollback rule. Close the incident only after seven complete days within 0.5 percentage points of baseline. There are no carried-over actions because this is the incident-opening review."},
                {"id": "actions-table", "type": "table", "tableId": "table-actions"},
                {"id": "further-questions", "type": "markdown", "body": "## Further Questions\n\n1. Did issuer response-code or route mapping change on 15 September?\n2. Can the pattern be reproduced across device software versions and controlled transit tests?\n3. Did affected users retry successfully through another device or channel?\n4. Are the yellow segments persistent after another complete week?"},
                {"id": "caveats", "type": "markdown", "body": "## Caveats and Assumptions\n\n- All data are deterministic, synthetic and aggregate; no personal or payment identifiers are included.\n- The dataset identifies where performance changed but does not contain logs or response codes needed to confirm technical cause.\n- Synthetic GMV is payment volume, not revenue or profit.\n- The four-week benchmark is a monitoring reference, not a contractual target.\n- Funnel and 30-day repeat metrics are excluded because the relevant cohorts are not mature at the reporting cutoff."},
            ],
        },
        "snapshot": {
            "version": 1,
            "status": "ready",
            "generatedAt": "2026-08-09T00:00:00+08:00",
            "datasets": {
                "kpi_summary": kpi_summary,
                "diagnostic_daily": data["diagnostic_daily_series"],
                "segment_rows": segment_rows,
                "action_rows": data["action_tracker"],
            },
        },
        "sources": [source, action_source],
    }
    return artifact


def main():
    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MARKDOWN_PATH.write_text(build_markdown(data), encoding="utf-8")
    ARTIFACT_PATH.write_text(
        json.dumps(build_artifact(data), indent=2), encoding="utf-8"
    )
    print(MARKDOWN_PATH)
    print(ARTIFACT_PATH)


if __name__ == "__main__":
    main()
