import re
import logging
from typing import Tuple, List, Optional

logger = logging.getLogger(__name__)

# List of allowed financial topics to keep the bot focused
ALLOWED_TOPICS = [
    "mutual fund", "sip", "nav", "zerodha", "groww", "investment", 
    "returns", "expense ratio", "exit load", "portfolio", "tax", 
    "elss", "equity", "debt", "hybrid", "gold", "amfi", "market",
    "human", "support", "help", "agent", "contact",
    "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
    "who are you", "what can you do", "features", "how are you"
]

# Simple patterns for prompt injection detection
INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"system prompt",
    r"you are now a",
    r"forget everything you know",
    r"reveal your hidden",
    r"jailbreak",
    r"dan mode"
]

class Guardrails:
    """Handles input and output safety checks for the chatbot."""

    @staticmethod
    def is_off_topic(query: str) -> bool:
        """Checks if the query is related to financial/mutual fund topics."""
        query_lower = query.lower()
        return not any(topic in query_lower for topic in ALLOWED_TOPICS)

    @staticmethod
    def detect_prompt_injection(query: str) -> bool:
        """Detects potential prompt injection attempts using regex patterns."""
        query_lower = query.lower()
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, query_lower):
                return True
        return False

    @staticmethod
    def validate_input(query: str) -> Tuple[bool, Optional[str]]:
        """
        Validates the user input against safety rules.
        Returns (is_safe, error_message).
        """
        if Guardrails.detect_prompt_injection(query):
            logger.warning(f"Prompt injection detected in query: {query}")
            return False, "I'm sorry, I cannot process this request due to security policies."

        if Guardrails.is_off_topic(query):
            logger.info(f"Off-topic query detected: {query}")
            return False, "I specialize in Zerodha Mutual Funds and financial planning. Please ask me something related to those topics!"

        return True, None

    @staticmethod
    def validate_output(response: str, query: str) -> str:
        """
        Performs post-generation checks on the response.
        Ensures disclaimers are present if financial advice is given.
        """
        if not isinstance(response, str):
            response = str(response)

        # Hard check for "guaranteed" returns - a big no-no in MF
        guarantee_patterns = [
            r"guarantee(d)? returns",
            r"fixed returns of \d+%",
            r"no risk",
            r"zero risk"
        ]
        
        for pattern in guarantee_patterns:
            if re.search(pattern, response.lower()):
                logger.warning(f"Hallucinated guarantee detected in response: {response}")
                response = response.replace(pattern, "expected (not guaranteed) returns")
                response += "\n\n**Note:** Mutual fund returns are never guaranteed."

        return response
