from langchain_community.tools import DuckDuckGoSearchRun
import sys

def search_scheme_codes():
    search = DuckDuckGoSearchRun()
    funds = [
        "HDFC Mid-Cap Opportunities Fund Direct Growth AMFI scheme code",
        "HDFC Small Cap Fund Direct Growth AMFI scheme code",
        "HDFC Flexi Cap Fund Direct Growth AMFI scheme code",
        "HDFC Multi Cap Fund Direct Growth AMFI scheme code",
        "HDFC Gold ETF Fund of Fund Direct Growth AMFI scheme code"
    ]
    
    for fund in funds:
        print(f"\nSearching for: {fund}")
        try:
            result = search.run(fund)
            # Encode and decode to handle potential character issues on Windows terminal
            print(result.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    search_scheme_codes()
