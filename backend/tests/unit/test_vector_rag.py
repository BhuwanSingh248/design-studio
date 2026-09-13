"""Unit tests for vector retrieval and chunking."""
from src.rag.chunker import DocumentChunker


def test_document_chunker():
    chunker = DocumentChunker()
    chunks = chunker.chunk_markdown("# SOLID\n\nContent here", "SOLID Principles")
    assert len(chunks) == 1
    assert chunks[0].title == "SOLID Principles"
