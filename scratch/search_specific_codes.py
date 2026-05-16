from duckduckgo_search import DDGS
import sys

def search_one(query):
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)
        for r in results:
            print(f"Snippet: {r['body']}")

if __name__ == "__main__":
    search_one("AMFI scheme code HDFC Small Cap Fund Direct Plan Growth")
    search_one("AMFI scheme code HDFC Multi Cap Fund Direct Plan Growth")
    search_one("AMFI scheme code HDFC Flexi Cap Fund Direct Plan Growth")
