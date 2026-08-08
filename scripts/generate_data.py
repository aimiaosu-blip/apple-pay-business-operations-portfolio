"""Deterministically regenerate aggregate, non-personal synthetic operations data."""
from pathlib import Path
from datetime import date,timedelta
import csv,random,sqlite3

ROOT=Path(__file__).resolve().parents[1];SEED=20260810
def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)

rng=random.Random(SEED);regions=['East China','North China','South China','West China'];issuers=['Issuer A','Issuer B','Issuer C','Issuer D'];cats=['Retail','Dining','Transit','Grocery','Digital'];devices=['Recent phone','Older phone','Watch'];facts=[];start=date(2025,1,1)
for di in range(365):
    d=start+timedelta(days=di);trend=1+.0014*di;weekend=1.10 if d.weekday()>=5 else 1
    for ri,region in enumerate(regions):
      for ii,issuer in enumerate(issuers):
       for ci,category in enumerate(cats):
        for vi,device in enumerate(devices):
         attempts=max(20,int((52+ri*8+ci*5-vi*7)*trend*weekend+rng.gauss(0,5)));rate=.965-ri*.002-vi*.006-ci*.001
         incident=date(2025,9,15)<=d<=date(2025,10,5) and region=='East China' and issuer=='Issuer B' and category=='Transit' and device=='Older phone'
         if incident:rate-=.115
         success=max(0,min(attempts,int(round(attempts*rate+rng.gauss(0,1)))));gmv=success*(18+ci*7+ri*2+rng.uniform(-2,2))
         facts.append(dict(date=d.isoformat(),region=region,issuer=issuer,merchant_category=category,device_segment=device,attempts=attempts,successful_transactions=success,failed_transactions=attempts-success,gmv_cny=round(gmv,2),is_anomaly_window=int(incident),is_synthetic=1))
write_csv(ROOT/'data/raw/fact_daily_operations_synthetic.csv',facts)
funnel=[]
for w in range(52):
    cohort=(start+timedelta(days=7*w)).isoformat();eligible=1200+18*w+rng.randint(-50,50);provision=int(eligible*(.62+.001*w));activated=int(provision*(.78+rng.uniform(-.015,.015)));first=int(activated*(.82+rng.uniform(-.012,.012)));repeat=int(first*(.64+.002*w+rng.uniform(-.015,.015)))
    funnel.append(dict(cohort_week=cohort,eligible_devices=eligible,provision_started=provision,activated=activated,first_transaction=first,repeat_30d=repeat,activation_rate=round(activated/eligible,4),first_txn_rate=round(first/activated,4),repeat_30d_rate=round(repeat/first,4)))
write_csv(ROOT/'data/raw/funnel_cohorts_synthetic.csv',funnel)
daily={};monthly={}
for r in facts:
    for key,b in [(r['date'],daily),(r['date'][:7],monthly)]:
        x=b.setdefault(key,dict(attempts=0,successful_transactions=0,failed_transactions=0,gmv_cny=0))
        for c in x:x[c]+=r[c]
drows=[{'date':k,**v,'success_rate':round(v['successful_transactions']/v['attempts'],5)} for k,v in sorted(daily.items())];mrows=[{'month':k,**v,'success_rate':round(v['successful_transactions']/v['attempts'],5)} for k,v in sorted(monthly.items())]
write_csv(ROOT/'data/processed/daily_kpis_bi.csv',drows);write_csv(ROOT/'data/processed/monthly_kpis_bi.csv',mrows)
db=ROOT/'data/apple_pay_operations.sqlite';db.unlink(missing_ok=True);con=sqlite3.connect(db)
con.execute('CREATE TABLE fact_daily_operations(date TEXT,region TEXT,issuer TEXT,merchant_category TEXT,device_segment TEXT,attempts INTEGER,successful_transactions INTEGER,failed_transactions INTEGER,gmv_cny REAL,is_anomaly_window INTEGER,is_synthetic INTEGER)');con.executemany('INSERT INTO fact_daily_operations VALUES (?,?,?,?,?,?,?,?,?,?,?)',[list(r.values()) for r in facts])
con.execute('CREATE TABLE funnel_cohorts(cohort_week TEXT,eligible_devices INTEGER,provision_started INTEGER,activated INTEGER,first_transaction INTEGER,repeat_30d INTEGER,activation_rate REAL,first_txn_rate REAL,repeat_30d_rate REAL)');con.executemany('INSERT INTO funnel_cohorts VALUES (?,?,?,?,?,?,?,?,?)',[list(r.values()) for r in funnel]);con.commit();con.close();print(f'regenerated with seed {SEED}')
