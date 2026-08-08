# Data Dictionary

## `fact_daily_operations`
Grain: one calendar day × region × synthetic issuer × merchant category × device segment. No person, card, account, merchant or transaction identifier exists.

| Field | Type | Meaning |
|---|---|---|
| date | date | Calendar date, 2025 |
| region | text | Broad synthetic operating region |
| issuer | text | Anonymized synthetic issuer label |
| merchant_category | text | Aggregated merchant category |
| device_segment | text | Coarse device group |
| attempts | integer | Authorization attempts |
| successful_transactions | integer | Attempts completing successfully |
| failed_transactions | integer | Attempts not completing |
| gmv_cny | numeric | Synthetic gross transaction value |
| is_anomaly_window | boolean | Deliberately planted diagnostic case |
| is_synthetic | boolean | Always true |

## `funnel_cohorts`
Grain: synthetic weekly eligibility cohort. Counts progress through provision start, activation, first transaction and 30-day repeat.
