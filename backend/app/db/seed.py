from sqlalchemy.orm import Session

from app.repositories.knowledge_repo import KnowledgeRepository


FAQS = [
    {
        "title": "Shipping to the USA",
        "category": "shipping",
        "content": (
            "Northstar Outfitters ships to all 50 US states. Standard shipping is free on orders over $75. "
            "Orders below $75 have a flat $6.95 standard shipping fee."
        ),
        "enabled": True,
    },
    {
        "title": "Delivery time",
        "category": "shipping",
        "content": (
            "Most standard US orders arrive in 3 to 6 business days after fulfillment. Expedited orders usually "
            "arrive in 1 to 2 business days after fulfillment."
        ),
        "enabled": True,
    },
    {
        "title": "Return policy",
        "category": "returns",
        "content": (
            "Unused items can be returned within 30 days of delivery with original tags and packaging. Final-sale "
            "items and used outdoor gear are not eligible for return."
        ),
        "enabled": True,
    },
    {
        "title": "Refund timing",
        "category": "returns",
        "content": (
            "Refunds are issued to the original payment method within 5 to 7 business days after the returned item "
            "is inspected and approved."
        ),
        "enabled": True,
    },
    {
        "title": "Support hours",
        "category": "support",
        "content": (
            "Customer support is available Monday through Friday, 9 AM to 6 PM Eastern Time. Email support is "
            "available at support@northstar.example."
        ),
        "enabled": True,
    },
    {
        "title": "Warranty",
        "category": "warranty",
        "content": (
            "Northstar Outfitters products include a one-year limited warranty covering manufacturing defects. "
            "Normal wear, misuse, and accidental damage are not covered."
        ),
        "enabled": True,
    },
    {
        "title": "Cancellation",
        "category": "orders",
        "content": (
            "Orders can be cancelled within 30 minutes of purchase if fulfillment has not started. After that, "
            "customers should follow the returns process once the order arrives."
        ),
        "enabled": True,
    },
    {
        "title": "Payment methods",
        "category": "payment",
        "content": (
            "Northstar Outfitters accepts major credit cards, debit cards, Apple Pay, Google Pay, and Northstar "
            "gift cards. Cash on delivery is not supported."
        ),
        "enabled": True,
    },
]


def seed_knowledge(db: Session) -> None:
    repo = KnowledgeRepository(db)
    if repo.count() > 0:
        return
    repo.bulk_create(FAQS)
    db.commit()
