"""
Sub-Phase 1A: Retriever Module
================================
Loads the FAISS vector index built in Phase 0, embeds user queries using the
same Google embedding model, performs similarity search, and returns the top-K
most relevant chunks with scores and metadata.

Usage (standalone):
    python -m src.retrieval.retriever
"""

import logging
import os
import re
from typing import List, Dict, Optional

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Known Zerodha fund names for metadata-based filtering
KNOWN_FUND_KEYWORDS = {
    "large midcap": "Zerodha Large Midcap",
    "large-midcap": "Zerodha Large Midcap",
    "index": "Zerodha",
    "silver": "Zerodha Silver",
    "gold": "Zerodha Gold",
    "gold etf": "Zerodha Gold",
    "elss": "Zerodha ELSS",
    "overnight": "Zerodha Overnight",
}


class Retriever:
    """Semantic search over the Phase 0 FAISS vector store."""

    def __init__(
        self,
        index_dir: str = "data/vector_store",
        top_k: int = 5,
        score_threshold: float = 0.5,
    ):
        """
        Args:
            index_dir: Path to the FAISS index directory (must contain index.faiss + index.pkl).
            top_k: Number of top chunks to return.
            score_threshold: Minimum similarity score to include a chunk (0-1 scale, higher is better).
        """
        self.index_dir = index_dir
        self.top_k = top_k
        self.score_threshold = score_threshold
        self._vector_store: Optional[FAISS] = None

        # Must use the exact same embedding model that Phase 0 embedder used
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY not found in environment.")
            raise ValueError("GOOGLE_API_KEY is required for the Retriever.")
            
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=api_key
        )

    def _load_index(self):
        """Load the FAISS index from disk. Fails fast if index doesn't exist."""
        if self._vector_store is not None:
            return  # already loaded

        index_path = os.path.join(self.index_dir, "index.faiss")
        if not os.path.exists(index_path):
            raise FileNotFoundError(
                f"FAISS index not found at '{self.index_dir}'. "
                "Run Phase 0 ingestion pipeline first: python scripts/run_ingestion.py"
            )

        logger.info(f"Loading FAISS index from {self.index_dir}...")
        self._vector_store = FAISS.load_local(
            self.index_dir,
            self.embeddings,
            allow_dangerous_deserialization=True,
        )
        logger.info("FAISS index loaded successfully.")

    def _detect_fund_filter(self, query: str) -> Optional[str]:
        """
        Check if the query mentions a specific HDFC fund by keyword.
        Returns a partial fund_name string to filter metadata, or None.
        """
        if not isinstance(query, str):
            query = str(query)
        query_lower = query.lower()

        for keyword, fund_prefix in KNOWN_FUND_KEYWORDS.items():
            if keyword in query_lower:
                logger.debug(f"Detected fund filter: '{keyword}' → '{fund_prefix}'")
                return fund_prefix
        return None

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
        fund_filter: Optional[str] = None,
    ) -> List[Dict]:
        """
        Retrieve the most relevant chunks for a given query.

        Args:
            query: The user's natural language question.
            top_k: Override default top-K (optional).
            score_threshold: Override default threshold (optional).
            fund_filter: Explicit fund name prefix to filter by (optional).
                         If None, auto-detects from the query text.

        Returns:
            A list of dicts, each containing:
              - text (str): The chunk content
              - metadata (dict): fund_name, scheme_code, chunk_id
              - score (float): Similarity score (higher = more relevant)
        """
        if not query:
            logger.warning("Empty query received. Returning no results.")
            return []
            
        if not isinstance(query, str):
            query = str(query)


        self._load_index()

        k = top_k or self.top_k
        threshold = score_threshold or self.score_threshold

        # Auto-detect fund filter from query if not explicitly provided
        if fund_filter is None:
            fund_filter = self._detect_fund_filter(query)

        # Fetch more candidates than top_k so we can filter by metadata and threshold
        fetch_k = k * 3 if fund_filter else k * 2

        logger.info(f"Searching for top-{k} chunks (threshold={threshold}, fund_filter={fund_filter})")

        try:
            results = self._vector_store.similarity_search_with_score(query, k=fetch_k)
        except Exception as e:
            logger.error(f"FAISS search failed: {e}")
            return []

        # Process results
        # NOTE: LangChain FAISS returns (Document, distance). Lower distance = more similar.
        # We convert distance to a 0-1 similarity score: score = 1 / (1 + distance)
        processed = []
        for doc, distance in results:
            score = 1.0 / (1.0 + distance)

            # Apply similarity threshold
            if score < threshold:
                continue

            # Apply fund name filter if detected
            if fund_filter:
                doc_fund = doc.metadata.get("fund_name", "")
                if doc_fund and fund_filter.lower() not in doc_fund.lower():
                    continue

            processed.append({
                "text": doc.page_content,
                "metadata": doc.metadata,
                "score": round(score, 4),
            })

        # Sort by score descending and take top-K
        processed.sort(key=lambda x: x["score"], reverse=True)
        results_out = processed[:k]

        logger.info(f"Retrieved {len(results_out)} chunks (from {len(results)} candidates).")
        return results_out

    def retrieve_formatted(self, query: str, **kwargs) -> str:
        """
        Convenience method: retrieve chunks and format them as a single context string
        for injection into an LLM prompt (used by Sub-Phase 1B).
        """
        chunks = self.retrieve(query, **kwargs)

        if not chunks:
            return "[No relevant information found in the knowledge base.]"

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            fund = chunk["metadata"].get("fund_name", "Unknown Fund")
            url = chunk["metadata"].get("groww_url", "N/A")
            score = chunk["score"]
            context_parts.append(
                f"--- Source {i} ({fund}, relevance: {score:.0%}) ---\n"
                f"URL: {url}\n"
                f"{chunk['text']}"
            )

        return "\n\n".join(context_parts)


# ─── Standalone execution for testing ─────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    retriever = Retriever()

    test_queries = [
        "What is the NAV of Zerodha Large Midcap 250?",
        "Tell me about Zerodha ELSS Tax Saver",
        "What is the expense ratio of Zerodha Gold ETF FoF?",
        "What is SIP?",
        "How does the Zerodha Overnight Fund work?",
    ]

    for q in test_queries:
        print(f"\n{'='*70}")
        print(f"QUERY: {q}")
        print(f"{'='*70}")

        results = retriever.retrieve(q)

        if not results:
            print("  ⚠️  No relevant chunks found.")
        else:
            for r in results:
                fund = r["metadata"].get("fund_name", "?")
                chunk_id = r["metadata"].get("chunk_id", "?")
                print(f"  [{r['score']:.0%}] {fund} (chunk #{chunk_id})")
                # Show first 120 chars of text
                preview = r["text"][:120].replace("\n", " ")
                print(f"       {preview}...")

        print()
