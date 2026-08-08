-- Weekly KPI
SELECT strftime('%Y-%W',date) AS year_week,SUM(attempts) attempts,SUM(successful_transactions) successful,1.0*SUM(successful_transactions)/SUM(attempts) success_rate,SUM(gmv_cny) gmv_cny FROM fact_daily_operations GROUP BY 1 ORDER BY 1;
-- Monthly KPI
SELECT substr(date,1,7) month,SUM(attempts) attempts,1.0*SUM(successful_transactions)/SUM(attempts) success_rate,SUM(gmv_cny) gmv_cny FROM fact_daily_operations GROUP BY 1 ORDER BY 1;
-- Funnel/cohort
SELECT cohort_week,1.0*activated/eligible_devices activation_rate,1.0*first_transaction/activated first_txn_rate,1.0*repeat_30d/first_transaction repeat_30d_rate FROM funnel_cohorts ORDER BY cohort_week;
-- Diagnostic cuts
SELECT region,issuer,merchant_category,device_segment,SUM(attempts) attempts,1.0*SUM(successful_transactions)/SUM(attempts) success_rate FROM fact_daily_operations WHERE date BETWEEN '2025-09-15' AND '2025-10-05' GROUP BY 1,2,3,4 HAVING SUM(attempts)>=500 ORDER BY success_rate LIMIT 20;
-- Anomaly baseline vs incident
WITH x AS (SELECT CASE WHEN date BETWEEN '2025-09-15' AND '2025-10-05' THEN 'incident' ELSE 'baseline' END period,SUM(attempts) attempts,SUM(successful_transactions) ok FROM fact_daily_operations WHERE region='East China' AND issuer='Issuer B' AND merchant_category='Transit' AND device_segment='Older phone' AND date BETWEEN '2025-08-25' AND '2025-10-05' GROUP BY 1) SELECT period,attempts,1.0*ok/attempts success_rate FROM x;
