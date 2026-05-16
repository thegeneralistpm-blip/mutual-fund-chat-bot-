from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import logging
import os
from typing import List, Dict

logger = logging.getLogger(__name__)

class VectorEmbedder:
    def __init__(self, save_dir: str = "data/vector_store"):
        self.save_dir = save_dir
        # Assumes GOOGLE_API_KEY is in environment
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        
    def embed_and_store(self, chunks: List[Dict]):
        """Creates embeddings for the chunks and saves them to a local FAISS index."""
        if not chunks:
            logger.warning("No chunks provided to embed.")
            return
            
        logger.info(f"Embedding {len(chunks)} chunks in batches...")
        documents = [Document(page_content=c["text"], metadata=c["metadata"]) for c in chunks]
        
        batch_size = 50
        vector_store = None
        
        import time
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1} ({(i/len(documents)):.1%})...")
            
            success = False
            retries = 3
            while not success and retries > 0:
                try:
                    if vector_store is None:
                        vector_store = FAISS.from_documents(batch, self.embeddings)
                    else:
                        vector_store.add_documents(batch)
                    success = True
                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        logger.warning("Quota hit, waiting 30s...")
                        time.sleep(30)
                        retries -= 1
                    else:
                        raise e
            
            if not success:
                raise Exception("Failed to embed after multiple retries due to quota limits.")

            # Small delay between batches even if successful
            time.sleep(2)
            
        if vector_store:
            os.makedirs(self.save_dir, exist_ok=True)
            vector_store.save_local(self.save_dir)
            logger.info(f"Successfully saved FAISS index to {self.save_dir}")
