from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import os
from dotenv import load_dotenv

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
doc = Document(page_content="test", metadata={"source": "test"})

try:
    print("Attempting to create FAISS index...")
    vs = FAISS.from_documents([doc], embeddings)
    vs.save_local("data/test_index")
    print("Success!")
except Exception as e:
    print(f"Failed: {e}")
