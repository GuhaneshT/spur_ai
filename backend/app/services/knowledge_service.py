import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import KnowledgeItem
from app.repositories.knowledge_repo import KnowledgeRepository


STOP_WORDS = {
    "a",
    "about",
    "an",
    "and",
    "are",
    "can",
    "do",
    "for",
    "how",
    "i",
    "in",
    "is",
    "it",
    "my",
    "of",
    "on",
    "the",
    "to",
    "what",
    "when",
    "with",
}


@dataclass(frozen=True)
class KnowledgeMatch:
    item: KnowledgeItem
    score: int


class KnowledgeService:
    def __init__(self, db: Session):
        self.repo = KnowledgeRepository(db)

    def relevant_items(self, message: str, limit: int = 3) -> list[KnowledgeItem]:
        terms = self._terms(message)
        matches: list[KnowledgeMatch] = []
        for item in self.repo.enabled_items():
            haystack = self._terms(f"{item.title} {item.category} {item.content}")
            score = sum(1 for term in terms if term in haystack)
            if score:
                matches.append(KnowledgeMatch(item=item, score=score))

        matches.sort(key=lambda match: match.score, reverse=True)
        return [match.item for match in matches[:limit]]

    def render_context(self, items: list[KnowledgeItem]) -> str:
        return "\n".join(f"- {item.title}: {item.content}" for item in items)

    def _terms(self, message: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[a-z0-9]+", message.lower())
            if len(token) > 2 and token not in STOP_WORDS
        }
