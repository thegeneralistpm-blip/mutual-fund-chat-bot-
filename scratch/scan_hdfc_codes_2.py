import sys
sys.path.append('.')
from src.ingestion.amfi_client import AMFIClient

client = AMFIClient()
codes = ['119058', '119059', '119060', '119061', '119062', '100034', '100035', '145550', '145551', '149940', '149941']

for c in codes:
    data = client.get_fund_data(c)
    if data:
        print(f"{c}: {data['meta']['scheme_name']}")
