from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .file_io import load_documents


@dataclass(frozen=True)
class ScoredExcerpt:
    title: str
    path: Path
    score: int
    excerpt: str


_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")
_SPLIT_RE = re.compile(r"\n\s*\n+")


def _tokenise(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN_RE.findall(text or "") if len(t) > 2}


def _chunk_text(text: str, max_chars: int = 1200) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []
    blocks = [b.strip() for b in _SPLIT_RE.split(text) if b.strip()]
    if not blocks:
        return [text[:max_chars]]
    chunks: list[str] = []
    current = ""
    for block in blocks:
        candidate = f"{current}\n\n{block}".strip() if current else block
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current.strip())
            if len(block) <= max_chars:
                current = block
            else:
                start = 0
                while start < len(block):
                    chunks.append(block[start:start + max_chars].strip())
                    start += max_chars
                current = ""
    if current:
        chunks.append(current.strip())
    return [c for c in chunks if c]


def gather_knowledge_base(knowledge_base_dir: str | Path, query: str, *, max_items: int = 4) -> str:
    base = Path(knowledge_base_dir)
    if not base.exists():
        return ""

    files = [p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".txt", ".docx", ".pdf"}]
    if not files:
        return ""

    docs = load_documents(files)
    query_tokens = _tokenise(query)
    if not query_tokens:
        query_tokens = _tokenise("knowledge base legal guidance contract research intake compliance summary")

    scored: list[ScoredExcerpt] = []
    for doc in docs:
        for chunk in _chunk_text(doc.text):
            chunk_tokens = _tokenise(chunk)
            score = len(query_tokens & chunk_tokens)
            if score <= 0:
                continue
            excerpt = " ".join(chunk.split())[:1200]
            scored.append(ScoredExcerpt(title=doc.title, path=doc.path, score=score, excerpt=excerpt))

    if not scored:
        fallback_docs = docs[:max_items]
        return "\n\n".join(f"[{doc.title}]\n{doc.text[:1200].strip()}" for doc in fallback_docs)

    scored.sort(key=lambda item: (item.score, len(item.excerpt)), reverse=True)
    top = scored[:max_items]
    blocks = []
    for item in top:
        blocks.append(f"[{item.title}]\nScore: {item.score}\n{item.excerpt}")
    return "\n\n".join(blocks)
