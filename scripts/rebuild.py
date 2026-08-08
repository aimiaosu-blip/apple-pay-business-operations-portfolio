from pathlib import Path
import sqlite3
root=Path(__file__).resolve().parents[1];con=sqlite3.connect(root/'data/apple_pay_operations.sqlite')
checks=[con.execute('SELECT COUNT(*) FROM fact_daily_operations').fetchone()[0]==87600,con.execute('SELECT COUNT(*) FROM fact_daily_operations WHERE attempts<>successful_transactions+failed_transactions OR is_synthetic<>1').fetchone()[0]==0,con.execute('SELECT COUNT(*) FROM funnel_cohorts').fetchone()[0]==52]
for q in (root/'sql/quality_tests.sql').read_text().split(';'):
    if q.strip(): con.execute(q)
con.close()
if not all(checks): raise SystemExit('validation failed')
print('digital wallet operations portfolio checks passed')
