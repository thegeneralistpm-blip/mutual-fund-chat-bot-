import logging
import os
import re
from typing import List, Dict, Union
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.exceptions import OutputParserException

from src.llm.prompt_templates import (
    SYSTEM_PROMPT,
    QA_PROMPT,
    SEBI_DISCLAIMER,
    FALLBACK_ERROR_MESSAGE,
)

load_dotenv()
logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Handles prompt construction and interaction with the Google Gemini LLM."""
    
    def __init__(self, temperature: float = 0.0):
        """
        Initializes the LLM. 
        Temperature is set to 0.0 to ensure deterministic, grounded responses.
        """
        self.temperature = temperature
        
        # Check API key without crashing
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY not found in environment. Generator will fail if called.")
            self.llm = None
        else:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    temperature=self.temperature,
                    max_retries=3,
                    timeout=30.0
                )
            except Exception as e:
                logger.error(f"Failed to initialize Gemini LLM: {e}")
                self.llm = None

    def _format_context(self, context_data: Union[str, List[Dict]]) -> str:
        """Helper to format retrieved chunks into a single string if needed."""
        if isinstance(context_data, str):
            return context_data
            
        if not context_data:
            return "[No relevant context found.]"
            
        context_parts = []
        for i, chunk in enumerate(context_data, 1):
            text = chunk.get("text", "")
            meta = chunk.get("metadata", {})
            fund = meta.get("fund_name", "Unknown Fund")
            context_parts.append(f"--- Source {i} ({fund}) ---\n{text}")
            
        return "\n\n".join(context_parts)

    def _needs_disclaimer(self, query: str, response: str) -> bool:
        """
        Simple heuristic to determine if the SEBI disclaimer is needed.
        Triggers if the query asks for performance, recommendations, or if the response mentions returns.
        """
        trigger_keywords = [
            "recommend", "suggest", "invest", "buy", "sell", "return", 
            "performance", "growth", "yield", "nav", "historical", "portfolio"
        ]
        
        combined_text = (query + " " + response).lower()
        for kw in trigger_keywords:
            if kw in combined_text:
                return True
        return False

    def generate(self, query: str, context_chunks: Union[str, List[Dict]], user_context: str = "") -> str:
        """
        Generates an answer using the provided query, retrieved context chunks, and user context.
        
        Args:
            query: The user's question.
            context_chunks: Pre-formatted context string or list of chunk dictionaries.
            user_context: Context about the user's portfolio and preferences.
            
        Returns:
            The final generated string with disclaimers if applicable.
        """
        if not self.llm:
            return "Configuration Error: Google API key is missing. Cannot generate response."
            
        if not query or not query.strip():
            return "Please ask a question."
            
        context_str = self._format_context(context_chunks)
        if not user_context:
            user_context = "No user portfolio context available."
        
        # Assemble the full prompt
        prompt_text = QA_PROMPT.format(
            system_prompt=SYSTEM_PROMPT,
            user_context=user_context,
            context=context_str,
            query=query
        )
        
        logger.info(f"Generating response for query: '{query}'")
        
        try:
            # Call the LLM
            # Since invoke expects a list of messages or a string, we pass the assembled prompt string.
            response = self.llm.invoke(prompt_text)
            response_text = response.content.strip()
            
            # Post-generation validation & disclaimer injection
            if self._needs_disclaimer(query, response_text):
                # Ensure we don't duplicate the disclaimer if the LLM hallucinated its own
                if "Past performance is not an indicator" not in response_text:
                    response_text += SEBI_DISCLAIMER
                    
            return response_text
            
        except Exception as e:
            logger.error(f"Unexpected error during generation: {e}")
            return FALLBACK_ERROR_MESSAGE

# ─── Standalone execution for testing ─────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
    # Mock context to test without needing the Retriever (which requires FAISS index)
    mock_context = [
        {
            "text": "HDFC Mid Cap Fund Direct Growth is an equity mutual fund scheme. Current NAV is ₹99.769 as of 12 May 2026. The expense ratio is 0.75%. The fund manager is Chirag Setalvad.",
            "metadata": {"fund_name": "HDFC Mid Cap Fund Direct Growth"}
        },
        {
            "text": "The minimum SIP investment for HDFC Mid Cap Fund is ₹100. It has historical returns of 0.75% over 1 year and -2.10% over 3 years.",
            "metadata": {"fund_name": "HDFC Mid Cap Fund Direct Growth"}
        }
    ]
    
    generator = ResponseGenerator()
    
    test_cases = [
        ("What is the NAV of the Mid Cap fund?", mock_context),
        ("Who is the fund manager?", mock_context),
        ("Should I invest all my money in this fund?", mock_context), # Should trigger disclaimer
        ("How to bake a cake?", mock_context), # Should trigger off-topic refusal
        ("What is the NAV of SBI Small Cap Fund?", mock_context), # Should say info not in context
    ]
    
    print("\n" + "="*80)
    print("Testing Phase 1B LLM Generator")
    print("="*80)
    
    for query, context in test_cases:
        print(f"\n[USER]: {query}")
        print("-" * 40)
        response = generator.generate(query, context)
        print(f"[BOT]:\n{response}")
        print("="*80)
