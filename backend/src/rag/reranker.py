"""Cross-encoder reranking pipeline."""
class CrossEncoderReranker:
    async def rerank(self, query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
        return candidates[:top_k]
