from duckduckgo_search import DDGS
import re

def get_codes():
    funds = [
        "HDFC Mid-Cap Opportunities Fund Direct Growth AMFI code",
        "HDFC Small Cap Fund Direct Growth AMFI code",
        "HDFC Flexi Cap Fund Direct Growth AMFI code",
        "HDFC Multi Cap Fund Direct Growth AMFI code",
        "HDFC Gold ETF Fund of Fund Direct Growth AMFI code"
    ]
    
    with DDGS() as ddgs:
        for fund in funds:
            print(f"\n{fund}:")
            results = ddgs.text(fund, max_results=5)
            for r in results:
                codes = re.findall(r'\b1[0-9]{5}\b', r['body'])
                if codes:
                    print(f"  Found potential codes in search results: {codes}")
                print(f"  Snippet: {r['body'][:200]}")

if __name__ == "__main__":
    get_codes()
