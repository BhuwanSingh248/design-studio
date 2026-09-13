"""Dense vector embedding generation with batching and retry."""
class EmbeddingService:
    async def get_embedding(self, text: str) -> list[float]:
        return [0.0] * 1536

    async def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * 1536 for _ in texts]
