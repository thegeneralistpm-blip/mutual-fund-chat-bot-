import sys
sys.path.append('.')
from src.ingestion.amfi_client import AMFIClient

client = AMFIClient()
# Scan a range of HDFC codes
for c in range(119050, 119080):
    data = client.get_fund_data(str(c))
    if data:
        print(f"{c}: {data['meta']['scheme_name']}")
