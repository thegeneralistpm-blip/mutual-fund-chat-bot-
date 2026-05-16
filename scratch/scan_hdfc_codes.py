import sys
sys.path.append('.')
from src.ingestion.amfi_client import AMFIClient

client = AMFIClient()
# Try common HDFC Direct Growth codes
# 119062: Hybrid Equity
# 118989: Mid Cap
# 101964: Flexi Cap?
# 119064: Small Cap?
codes = ['118989', '119064', '119065', '119066', '119067', '119068', '119069', '119070', '101964', '101965']

for c in codes:
    data = client.get_fund_data(c)
    if data:
        print(f"{c}: {data['meta']['scheme_name']}")
