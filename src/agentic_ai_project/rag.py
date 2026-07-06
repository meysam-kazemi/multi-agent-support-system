"""Knowledge-base retrieval for the technical support agent."""

from __future__ import annotations

from pathlib import Path

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter


DEFAULT_KB_PATH = Path(__file__).resolve().parents[2] / "docs" / "mock_technical_support_knowledge_base.md"


def build_vector_store(kb_path: Path = DEFAULT_KB_PATH) -> InMemoryVectorStore:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = InMemoryVectorStore(embeddings)

    doc = kb_path.read_text(encoding="utf-8")
    markdown_splitter = MarkdownHeaderTextSplitter(
        [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
    )
    chunks = markdown_splitter.split_text(doc)
    vector_store.add_documents(documents=chunks)
    return vector_store
