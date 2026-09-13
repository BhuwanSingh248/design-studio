"""Query transformation and semantic expansion."""
class QueryTransformer:
    @staticmethod
    def expand_query(raw_query: str) -> str:
        return f"{raw_query} software design pattern SOLID"
