import uvicorn

if __name__ == "__main__":
    print("Starting Groww HDFC MF Chatbot API...")
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
