from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class TextChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 100):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        
    def chunk_documents(self, normalized_data_list: List[Dict]) -> List[Dict]:
        """Splits the full text of each fund into chunks while keeping metadata."""
        all_chunks = []
        
        for data in normalized_data_list:
            text = data.get("document_text", "")
            if not text:
                continue
                
            chunks = self.splitter.split_text(text)
            logger.info(f"Split {data.get('fund_name', 'Unknown Fund')} into {len(chunks)} chunks.")
            
            for i, chunk_text in enumerate(chunks):
                # Create a chunk object with text and metadata
                chunk = {
                    "text": chunk_text,
                    "metadata": {
                        "scheme_code": data.get("scheme_code"),
                        "fund_name": data.get("fund_name"),
                        "category": data.get("category"),
                        "groww_url": data.get("groww_url"),
                        "chunk_id": i
                    }
                }
                all_chunks.append(chunk)
                
        return all_chunks
