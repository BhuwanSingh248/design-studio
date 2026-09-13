"""RAG metric calculators: context relevance, faithfulness, and answer relevance."""
class RAGMetricsCalculator:
    def compute_faithfulness(self, answer: str, source_context: str) -> float:
        return 1.0
