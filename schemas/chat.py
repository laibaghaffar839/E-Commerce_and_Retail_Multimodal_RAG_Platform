from pydantic import BaseModel
from typing import List


class ChatRequest(BaseModel):
    query: str


class Source(BaseModel):
    filename: str
    file_type: str
    chunk_index: int
    excerpt: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]