from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import KnowledgeItem


class KnowledgeRepository:
    def __init__(self, db: Session):
        self.db = db

    def enabled_items(self) -> list[KnowledgeItem]:
        statement = select(KnowledgeItem).where(KnowledgeItem.enabled.is_(True)).order_by(KnowledgeItem.id.asc())
        return list(self.db.scalars(statement).all())

    def count(self) -> int:
        return len(self.db.scalars(select(KnowledgeItem.id)).all())

    def bulk_create(self, items: list[dict[str, str | bool]]) -> None:
        self.db.add_all(KnowledgeItem(**item) for item in items)