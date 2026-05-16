import sys
sys.path.append('.')
from src.ingestion.amfi_client import AMFIClient

client = AMFIClient()
codes = ["119598", "100033", "118989", "145550", "149940", "119063", "119061", "119062", "119065", "119066"]

for code in codes:
    try:
        data = client.get_fund_data(code)
        if data:
            print(f"{code}: {data['meta']['scheme_name']}")
        else:
            print(f"{code}: No data")
    except Exception as e:
        print(f"{code}: Error {e}")
