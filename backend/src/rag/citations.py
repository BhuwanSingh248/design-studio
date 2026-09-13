"""Prompt citation formatting and response citation parsing."""
class CitationEngine:
    @staticmethod
    def format_sources(chunks: list[dict]) -> str:
        return "\n".join(f"[Source {i+1}]: {c.get('content')}" for i, c in enumerate(chunks))
