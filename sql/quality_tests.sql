SELECT COUNT(*) AS invalid_balances FROM fact_daily_operations WHERE attempts<>successful_transactions+failed_transactions OR successful_transactions>attempts;
SELECT COUNT(*) AS non_synthetic FROM fact_daily_operations WHERE is_synthetic<>1;
SELECT COUNT(*) AS duplicate_grain FROM (SELECT date,region,issuer,merchant_category,device_segment FROM fact_daily_operations GROUP BY 1,2,3,4,5 HAVING COUNT(*)>1);
SELECT COUNT(*) AS invalid_funnel FROM funnel_cohorts WHERE repeat_30d>first_transaction OR first_transaction>activated OR activated>provision_started OR provision_started>eligible_devices;
