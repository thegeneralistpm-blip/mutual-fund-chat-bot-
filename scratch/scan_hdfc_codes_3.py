import sys
sys.path.append('.')
from src.ingestion.amfi_client import AMFIClient

client = AMFIClient()
codes = ['120641', '150838', '119063', '119065', '119060', '118989']

for c in codes:
    data = client.get_fund_data(c)
    if data:
        print(f"{c}: {data['meta']['scheme_name']}")
