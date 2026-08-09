-- Apple Pay Business Operations Portfolio
-- Advanced SQL query pack: joins, rolling windows, LAG, ranking and contribution analysis.
-- SQLite-compatible; all source data are synthetic.

-- 1) Multi-table JOIN: align weekly payment operations with acquisition cohorts.
-- The cohort table is weekly and portfolio-wide, while operations are aggregated
-- to the same weekly grain before the join to avoid a many-to-many duplication.
WITH weekly_operations AS (
  SELECT
    date(date, '-' || ((CAST(strftime('%w', date) AS INTEGER) + 6) % 7) || ' days') AS week_start,
    SUM(attempts) AS attempts,
    SUM(successful_transactions) AS successful_transactions,
    SUM(failed_transactions) AS failed_transactions,
    SUM(gmv_cny) AS gmv_cny
  FROM fact_daily_operations
  GROUP BY 1
)
SELECT
  w.week_start,
  w.attempts,
  w.successful_transactions,
  1.0 * w.successful_transactions / NULLIF(w.attempts, 0) AS payment_success_rate,
  w.gmv_cny,
  f.eligible_devices,
  f.activated,
  f.first_transaction,
  f.repeat_30d,
  f.activation_rate,
  f.first_txn_rate,
  f.repeat_30d_rate
FROM weekly_operations w
LEFT JOIN funnel_cohorts f
  ON f.cohort_week = w.week_start
ORDER BY w.week_start;

-- 2) Window functions: daily KPI plus trailing 28-day success rate and GMV.
WITH daily AS (
  SELECT
    date,
    SUM(attempts) AS attempts,
    SUM(successful_transactions) AS successful_transactions,
    SUM(failed_transactions) AS failed_transactions,
    SUM(gmv_cny) AS gmv_cny
  FROM fact_daily_operations
  GROUP BY date
)
SELECT
  date,
  attempts,
  successful_transactions,
  1.0 * successful_transactions / NULLIF(attempts, 0) AS daily_success_rate,
  1.0 * SUM(successful_transactions) OVER (
    ORDER BY date ROWS BETWEEN 27 PRECEDING AND CURRENT ROW
  ) / NULLIF(
    SUM(attempts) OVER (ORDER BY date ROWS BETWEEN 27 PRECEDING AND CURRENT ROW),
    0
  ) AS rolling_28d_success_rate,
  SUM(gmv_cny) OVER (
    ORDER BY date ROWS BETWEEN 27 PRECEDING AND CURRENT ROW
  ) AS rolling_28d_gmv_cny
FROM daily
ORDER BY date;

-- 3) LAG: month-over-month attempts, GMV and success-rate movement.
WITH monthly AS (
  SELECT
    substr(date, 1, 7) AS month,
    SUM(attempts) AS attempts,
    SUM(successful_transactions) AS successful_transactions,
    SUM(gmv_cny) AS gmv_cny
  FROM fact_daily_operations
  GROUP BY 1
), with_rates AS (
  SELECT
    *,
    1.0 * successful_transactions / NULLIF(attempts, 0) AS success_rate
  FROM monthly
)
SELECT
  month,
  attempts,
  gmv_cny,
  success_rate,
  1.0 * attempts / NULLIF(LAG(attempts) OVER (ORDER BY month), 0) - 1 AS attempts_mom,
  1.0 * gmv_cny / NULLIF(LAG(gmv_cny) OVER (ORDER BY month), 0) - 1 AS gmv_mom,
  success_rate - LAG(success_rate) OVER (ORDER BY month) AS success_rate_change_pp
FROM with_rates
ORDER BY month;

-- 4) DENSE_RANK: rank issuer performance inside each region for the latest 28 days.
WITH cutoff AS (
  SELECT date(MAX(date), '-27 days') AS start_date, MAX(date) AS end_date
  FROM fact_daily_operations
), issuer_kpis AS (
  SELECT
    region,
    issuer,
    SUM(attempts) AS attempts,
    SUM(successful_transactions) AS successful_transactions,
    SUM(failed_transactions) AS failed_transactions,
    1.0 * SUM(successful_transactions) / NULLIF(SUM(attempts), 0) AS success_rate
  FROM fact_daily_operations, cutoff
  WHERE date BETWEEN cutoff.start_date AND cutoff.end_date
  GROUP BY region, issuer
)
SELECT
  *,
  DENSE_RANK() OVER (PARTITION BY region ORDER BY success_rate DESC) AS success_rank_in_region,
  DENSE_RANK() OVER (PARTITION BY region ORDER BY failed_transactions DESC) AS failure_volume_rank_in_region
FROM issuer_kpis
ORDER BY region, success_rank_in_region, issuer;

-- 5) Contribution analysis: which segment combinations explain excess failures?
-- Expected failures use each segment's baseline failure rate outside anomaly windows.
WITH segment AS (
  SELECT
    region,
    issuer,
    merchant_category,
    device_segment,
    SUM(CASE WHEN is_anomaly_window = 0 THEN failed_transactions ELSE 0 END) AS baseline_failures,
    SUM(CASE WHEN is_anomaly_window = 0 THEN attempts ELSE 0 END) AS baseline_attempts,
    SUM(CASE WHEN is_anomaly_window = 1 THEN failed_transactions ELSE 0 END) AS anomaly_failures,
    SUM(CASE WHEN is_anomaly_window = 1 THEN attempts ELSE 0 END) AS anomaly_attempts
  FROM fact_daily_operations
  GROUP BY region, issuer, merchant_category, device_segment
), excess AS (
  SELECT
    *,
    1.0 * baseline_failures / NULLIF(baseline_attempts, 0) AS baseline_failure_rate,
    anomaly_failures - anomaly_attempts * (
      1.0 * baseline_failures / NULLIF(baseline_attempts, 0)
    ) AS excess_failures
  FROM segment
)
SELECT
  region,
  issuer,
  merchant_category,
  device_segment,
  baseline_failure_rate,
  anomaly_failures,
  excess_failures,
  1.0 * excess_failures / NULLIF(SUM(excess_failures) OVER (), 0) AS excess_failure_contribution,
  DENSE_RANK() OVER (ORDER BY excess_failures DESC) AS contribution_rank
FROM excess
WHERE excess_failures > 0
ORDER BY contribution_rank, region, issuer;

