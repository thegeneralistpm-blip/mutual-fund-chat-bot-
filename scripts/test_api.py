import httpx
import json

def test_chat():
    url = "http://127.0.0.1:8000/chat"
    payload = {
        "query": "What is the NAV of HDFC Mid Cap Fund?"
    }
    
    try:
        print(f"Sending query to {url}...")
        response = httpx.post(url, json=payload, timeout=30.0)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nAnswer:")
            print(data["answer"])
            print("\nSources:")
            for s in data["sources"]:
                print(f"- {s['fund_name']} (Score: {s['score']})")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_chat()
