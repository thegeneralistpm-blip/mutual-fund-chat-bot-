from duckduckgo_search import DDGS

def get_codes():
    with DDGS() as ddgs:
        results = ddgs.text("site:amfiindia.com HDFC Small Cap Fund Direct Growth", max_results=5)
        for r in results:
            print(f"Snippet: {r['body']}")

if __name__ == "__main__":
    get_codes()
