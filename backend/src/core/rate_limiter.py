"""Rate limiting and token quota management."""
from dataclasses import dataclass


@dataclass
class TokenQuota:
    daily_budget_tokens: int = 1_000_000
    consumed_tokens: int = 0

    def check_and_consume(self, tokens: int) -> bool:
        if self.consumed_tokens + tokens > self.daily_budget_tokens:
            return False
        self.consumed_tokens += tokens
        return True
