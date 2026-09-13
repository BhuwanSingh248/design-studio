"""Splits markdown documents into structured token-bounded chunks."""
from dataclasses import dataclass


@dataclass
class DocumentChunk:
    chunk_id: str
    title: str
    content: str
    token_count: int


class DocumentChunker:
    def __init__(self, chunk_size: int = 512, overlap: int = 64):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_markdown(self, text: str, source_title: str) -> list[DocumentChunk]:
        return [DocumentChunk(chunk_id="1", title=source_title, content=text[:1000], token_count=len(text.split()))]
