import re
import logging

logger = logging.getLogger(__name__)

# PAN card: 5 letters, 4 digits, 1 letter
PAN_PATTERN = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
# Aadhaar: 12 digits (with optional spaces/dashes)
AADHAAR_PATTERN = r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b"
# Phone: 10 digits starting with 6-9
PHONE_PATTERN = r"\b[6-9]\d{9}\b"
# Email: simple pattern
EMAIL_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

class PIIRedactor:
    """Masks sensitive user data like PAN, Aadhaar, and Phone numbers."""

    @staticmethod
    def redact(text: str) -> str:
        """Redacts sensitive information from the given text."""
        if not text:
            return text
            
        redacted = text
        
        # Redact PAN
        redacted = re.sub(PAN_PATTERN, "[PAN_REDACTED]", redacted, flags=re.IGNORECASE)
        
        # Redact Aadhaar
        redacted = re.sub(AADHAAR_PATTERN, "[AADHAAR_REDACTED]", redacted)
        
        # Redact Phone
        redacted = re.sub(PHONE_PATTERN, "[PHONE_REDACTED]", redacted)
        
        # Redact Email
        redacted = re.sub(EMAIL_PATTERN, "[EMAIL_REDACTED]", redacted)
        
        if redacted != text:
            logger.info("PII detected and redacted from message.")
            
        return redacted
