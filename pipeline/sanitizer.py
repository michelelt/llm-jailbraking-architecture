import re

class Sanitizer:
    """
    Sanitizes text by redacting sensitive information and ensuring 
    compliance with safety reporting standards.
    """
    def __init__(self):
        # List of mock sensitive terms to redact
        self.sensitive_terms = [
            "sarin", "ricin", "anthrax", "mustard gas", "vx gas", 
            "botulinum", "tabun", "ebola", "yersinia pestis",
            "bomb", "explosive", "shrapnel"
        ]

    def sanitize(self, text: str) -> str:
        """
        Redacts sensitive terms from the text.
        """
        if not text:
            return ""
            
        sanitized_text = text
        for term in self.sensitive_terms:
            # Case insensitive replacement
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            sanitized_text = pattern.sub("[REDACTED]", sanitized_text)
            
        return sanitized_text
