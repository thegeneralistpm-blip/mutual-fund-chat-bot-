import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

def test_models():
    api_key = os.environ.get("GOOGLE_API_KEY")
    models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    
    for model in models:
        print(f"Testing {model}...")
        try:
            llm = ChatGoogleGenerativeAI(model=model, google_api_key=api_key)
            res = llm.invoke("Hi")
            print(f"  Success: {res.content[:50]}")
        except Exception as e:
            print(f"  Failed: {e}")

if __name__ == "__main__":
    test_models()
