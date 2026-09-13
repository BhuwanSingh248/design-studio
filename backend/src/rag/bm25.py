"""BM25 lexical index for exact identifier matching."""
class BM25Index:
    def __init__(self):
        self.corpus = []

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        return []
