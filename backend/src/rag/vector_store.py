"""PostgreSQL pgvector storage and similarity query engine."""
class VectorStore:
    async def similarity_search(self, query_vector: list[float], top_k: int = 5) -> list[dict]:
        return []
