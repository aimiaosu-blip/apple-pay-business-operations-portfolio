"""Build a reproducible weekly business review from the synthetic SQLite data."""

from __future__ import annotations

from datetime import date, timedelta
import json
from pathlib import Path
import sqlite3


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data/apple_pay_operations.sqlite"
OUTPUT_PATH = ROOT / "data/processed/weekly_business_review_2025_w38.json"
REPORT_START = date(2025, 9, 15)
REPORT_END = REPORT_START + timedelta(days=6)
PRIOR_START = REPORT_START - timedelta(days=7)
PRIOR_END = REPORT_START - timedelta(days=1)
BASELINE_START = REPORT_START - timedelta(days=28)
BASELINE_END = REPORT_START - timedelta(days=1)

AFFECTED_FILTER = {
    "region": "East China",
    "issuer": "Issuer B",
    "merchant_category": "Transit",
    "device_segment": "Older phone",
}


def period_summary(connection: sqlite3.Connection, start: date, end: date, extra=""):
    row = connection.execute(
        f"""
        SELECT
          SUM(attempts),
          SUM(successful_transactions),
          SUM(failed_transactions),
          SUM(gmv_cny)
        FROM fact_daily_operations
        WHERE date BETWEEN ? AND ? {extra}
        """,
        (start.isoformat(), end.isoformat()),
    ).fetchone()
    attempts, successful, failed, gmv = row
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "attempts": attempts,
        "successful_transactions": successful,
        "failed_transactions": failed,
        "success_rate": successful / attempts,
        "failure_rate": failed / attempts,
        "gmv_cny": round(gmv, 2),
    }


def change(current: float, comparison: float):
    return {
        "absolute": current - comparison,
        "relative": (current / comparison - 1) if comparison else None,
    }


def daily_series(connection: sqlite3.Connection):
    rows = connection.execute(
        """
        SELECT
          date,
          SUM(attempts) AS attempts,
          SUM(successful_transactions) AS successful_transactions,
          1.0 * SUM(successful_transactions) / SUM(attempts) AS success_rate,
          SUM(failed_transactions) AS failed_transactions,
          SUM(gmv_cny) AS gmv_cny
        FROM fact_daily_operations
        WHERE date BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date
        """,
        (BASELINE_START.isoformat(), REPORT_END.isoformat()),
    ).fetchall()
    return [
        {
            "date": row[0],
            "period": "Current week" if row[0] >= REPORT_START.isoformat() else "Baseline",
            "attempts": row[1],
            "successful_transactions": row[2],
            "success_rate": row[3],
            "failed_transactions": row[4],
            "gmv_cny": round(row[5], 2),
        }
        for row in rows
    ]


def segment_comparison(connection: sqlite3.Connection):
    current = connection.execute(
        """
        SELECT region, issuer, merchant_category, device_segment,
               SUM(attempts), SUM(successful_transactions)
        FROM fact_daily_operations
        WHERE date BETWEEN ? AND ?
        GROUP BY region, issuer, merchant_category, device_segment
        """,
        (REPORT_START.isoformat(), REPORT_END.isoformat()),
    ).fetchall()
    baseline = connection.execute(
        """
        SELECT region, issuer, merchant_category, device_segment,
               SUM(attempts), SUM(successful_transactions)
        FROM fact_daily_operations
        WHERE date BETWEEN ? AND ?
        GROUP BY region, issuer, merchant_category, device_segment
        """,
        (BASELINE_START.isoformat(), BASELINE_END.isoformat()),
    ).fetchall()
    baseline_map = {
        tuple(row[:4]): {"attempts": row[4], "successful": row[5]} for row in baseline
    }
    output = []
    for row in current:
        key = tuple(row[:4])
        attempts = row[4]
        successful = row[5]
        baseline_row = baseline_map[key]
        current_rate = successful / attempts
        baseline_rate = baseline_row["successful"] / baseline_row["attempts"]
        output.append(
            {
                "segment": " / ".join(key),
                "region": key[0],
                "issuer": key[1],
                "merchant_category": key[2],
                "device_segment": key[3],
                "attempts": attempts,
                "success_rate": current_rate,
                "baseline_success_rate": baseline_rate,
                "delta_pp": (current_rate - baseline_rate) * 100,
                "status": (
                    "LOW VOLUME"
                    if attempts < 500
                    else "RED"
                    if current_rate - baseline_rate <= -0.02
                    else "YELLOW"
                    if current_rate - baseline_rate <= -0.005
                    else "GREEN"
                ),
            }
        )
    return sorted(output, key=lambda item: item["delta_pp"])


def diagnostic_daily_series(connection: sqlite3.Connection):
    rows = []
    for label, extra in [
        (
            "Affected segment",
            """
            AND region='East China'
            AND issuer='Issuer B'
            AND merchant_category='Transit'
            AND device_segment='Older phone'
            """,
        ),
        (
            "Rest of portfolio",
            """
            AND NOT (
              region='East China'
              AND issuer='Issuer B'
              AND merchant_category='Transit'
              AND device_segment='Older phone'
            )
            """,
        ),
    ]:
        result = connection.execute(
            f"""
            SELECT date, SUM(attempts), SUM(successful_transactions)
            FROM fact_daily_operations
            WHERE date BETWEEN ? AND ? {extra}
            GROUP BY date
            ORDER BY date
            """,
            (BASELINE_START.isoformat(), REPORT_END.isoformat()),
        ).fetchall()
        for row in result:
            rows.append(
                {
                    "date": row[0],
                    "series": label,
                    "attempts": row[1],
                    "successful_transactions": row[2],
                    "success_rate": row[2] / row[1],
                    "period": (
                        "Current week"
                        if row[0] >= REPORT_START.isoformat()
                        else "Trailing baseline"
                    ),
                }
            )
    return rows


def funnel_comparison(connection: sqlite3.Connection):
    rows = connection.execute(
        """
        SELECT cohort_week, eligible_devices, activated, first_transaction,
               repeat_30d, activation_rate, first_txn_rate, repeat_30d_rate
        FROM funnel_cohorts
        WHERE cohort_week IN ('2025-09-10', '2025-09-17')
        ORDER BY cohort_week
        """
    ).fetchall()
    return [
        {
            "cohort_week": row[0],
            "eligible_devices": row[1],
            "activated": row[2],
            "first_transaction": row[3],
            "repeat_30d": row[4],
            "activation_rate": row[5],
            "first_txn_rate": row[6],
            "repeat_30d_rate": row[7],
        }
        for row in rows
    ]


def main():
    connection = sqlite3.connect(DB_PATH)
    current = period_summary(connection, REPORT_START, REPORT_END)
    prior = period_summary(connection, PRIOR_START, PRIOR_END)
    baseline = period_summary(connection, BASELINE_START, BASELINE_END)

    affected_where = """
      AND region='East China'
      AND issuer='Issuer B'
      AND merchant_category='Transit'
      AND device_segment='Older phone'
    """
    affected_current = period_summary(
        connection, REPORT_START, REPORT_END, affected_where
    )
    affected_prior = period_summary(connection, PRIOR_START, PRIOR_END, affected_where)
    affected_baseline = period_summary(
        connection, BASELINE_START, BASELINE_END, affected_where
    )

    rest_where = """
      AND NOT (
        region='East China'
        AND issuer='Issuer B'
        AND merchant_category='Transit'
        AND device_segment='Older phone'
      )
    """
    rest_current = period_summary(connection, REPORT_START, REPORT_END, rest_where)
    rest_baseline = period_summary(connection, BASELINE_START, BASELINE_END, rest_where)

    expected_affected_successes = (
        affected_current["attempts"] * affected_baseline["success_rate"]
    )
    excess_affected_failures = (
        expected_affected_successes - affected_current["successful_transactions"]
    )

    quality = connection.execute(
        """
        SELECT
          COUNT(*),
          SUM(CASE WHEN attempts <> successful_transactions + failed_transactions THEN 1 ELSE 0 END),
          SUM(CASE WHEN is_synthetic <> 1 THEN 1 ELSE 0 END),
          COUNT(DISTINCT region),
          COUNT(DISTINCT issuer),
          COUNT(DISTINCT merchant_category),
          COUNT(DISTINCT device_segment)
        FROM fact_daily_operations
        WHERE date BETWEEN ? AND ?
        """,
        (REPORT_START.isoformat(), REPORT_END.isoformat()),
    ).fetchone()

    segments = segment_comparison(connection)
    report = {
        "report": {
            "title": "Digital Wallet Weekly Business Review — Week 38, 2025",
            "reporting_period": f"{REPORT_START.isoformat()} to {REPORT_END.isoformat()}",
            "comparison_period": f"{PRIOR_START.isoformat()} to {PRIOR_END.isoformat()}",
            "baseline_period": f"{BASELINE_START.isoformat()} to {BASELINE_END.isoformat()}",
            "generated_from_seed": 20260810,
            "scope": "Aggregate deterministic synthetic portfolio data",
        },
        "current": current,
        "prior": prior,
        "baseline_4w": baseline,
        "changes": {
            "attempts_vs_prior": change(current["attempts"], prior["attempts"]),
            "success_rate_vs_prior": change(
                current["success_rate"], prior["success_rate"]
            ),
            "success_rate_vs_baseline": change(
                current["success_rate"], baseline["success_rate"]
            ),
            "failed_vs_prior": change(
                current["failed_transactions"], prior["failed_transactions"]
            ),
            "gmv_vs_prior": change(current["gmv_cny"], prior["gmv_cny"]),
        },
        "affected_segment": {
            "filter": AFFECTED_FILTER,
            "current": affected_current,
            "prior": affected_prior,
            "baseline_4w": affected_baseline,
            "delta_vs_baseline_pp": (
                affected_current["success_rate"]
                - affected_baseline["success_rate"]
            )
            * 100,
            "estimated_excess_failures_vs_baseline": round(
                excess_affected_failures, 1
            ),
        },
        "rest_of_portfolio": {
            "current": rest_current,
            "baseline_4w": rest_baseline,
            "delta_vs_baseline_pp": (
                rest_current["success_rate"] - rest_baseline["success_rate"]
            )
            * 100,
        },
        "daily_series": daily_series(connection),
        "diagnostic_daily_series": diagnostic_daily_series(connection),
        "lowest_segments": [
            segment for segment in segments if segment["attempts"] >= 500
        ][:8],
        "funnel_cohorts": funnel_comparison(connection),
        "data_quality": {
            "rows_in_report_week": quality[0],
            "transaction_balance_errors": quality[1],
            "non_synthetic_rows": quality[2],
            "regions": quality[3],
            "issuers": quality[4],
            "merchant_categories": quality[5],
            "device_segments": quality[6],
            "status": "GREEN"
            if quality[1] == 0 and quality[2] == 0 and quality[0] == 1680
            else "RED",
        },
        "status_rules": {
            "RED": "At least 500 weekly attempts and success rate >=2.0 percentage points below the trailing four-week baseline.",
            "YELLOW": "At least 500 weekly attempts and success rate 0.5–2.0 percentage points below baseline, or an open material incident affects the portfolio.",
            "GREEN": "Within 0.5 percentage points of baseline with complete reconciled data.",
        },
        "operating_status": {
            "overall": "YELLOW",
            "portfolio_success_rate": "YELLOW",
            "attempts": "GREEN",
            "gmv": "GREEN",
            "affected_segment": "RED",
            "data_quality": "GREEN",
            "basis": "Topline remains within 0.5 percentage points of baseline, but one high-volume segment has an open red breach.",
        },
        "action_tracker": [
            {
                "priority": 1,
                "action": "Validate issuer response-code and route mapping for the affected cut",
                "owner": "Payments Operations",
                "due_date": "2025-09-16",
                "status": "IN PROGRESS",
                "validation_metric": "Mapping review completed with evidence log",
            },
            {
                "priority": 2,
                "action": "Reproduce the issue across issuer, transit and older-device test cases",
                "owner": "Engineering + Issuer Partner",
                "due_date": "2025-09-17",
                "status": "IN PROGRESS",
                "validation_metric": "Failure pattern reproduced or ruled out",
            },
            {
                "priority": 3,
                "action": "Prepare a bounded configuration fix and rollback decision",
                "owner": "Product Operations",
                "due_date": "2025-09-19",
                "status": "PLANNED",
                "validation_metric": "Approved change and rollback criteria",
            },
            {
                "priority": 4,
                "action": "Monitor recovery and close only after seven complete days",
                "owner": "Business Analytics",
                "due_date": "2025-09-28",
                "status": "NOT STARTED",
                "validation_metric": "Success rate within 0.5pp of baseline for 7 days",
            },
        ],
    }
    connection.close()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
