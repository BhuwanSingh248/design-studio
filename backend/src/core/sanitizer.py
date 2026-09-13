"""Input sanitization and prompt injection defense."""
import re


class PromptSanitizer:
    FORBIDDEN_PATTERNS = [
        r"ignore all previous instructions",
        r"system prompt override",
        r"disregard rules",
    ]

    @classmethod
    def sanitize(cls, text: str) -> str:
        """Strip malicious injection patterns."""
        sanitized = text
        for pattern in cls.FORBIDDEN_PATTERNS:
            sanitized = re.sub(pattern, "[FILTERED]", sanitized, flags=re.IGNORECASE)
        return sanitized.strip()
