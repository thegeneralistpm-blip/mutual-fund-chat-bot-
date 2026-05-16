from duckduckgo_search import DDGS

def test_ddgs():
    with DDGS() as ddgs:
        results = ddgs.text("HDFC Mid-Cap Opportunities Fund Direct Growth AMFI code", max_results=5)
        for r in results:
            print(r)

if __name__ == "__main__":
    test_ddgs()
