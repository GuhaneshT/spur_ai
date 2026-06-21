import asyncio
import time
from dataclasses import dataclass, field
from typing import Protocol

from openai import AsyncOpenAI

from app.core.config import get_settings
from app.models import KnowledgeItem, Message
from app.services.token_budget import estimate_tokens


HANDOFF_REPLY = (
    "I may need a teammate to help with this specific issue. Please contact support at "
    "support@northstar.example."
)

SENSITIVE_OR_ORDER_TERMS = {
    "address",
    "card",
    "chargeback",
    "credit card",
    "fraud",
    "order number",
    "password",
    "refund status",
    "tracking number",
}

SYSTEM_PROMPT = """You are the live chat support agent for Northstar Outfitters.
Answer only from the provided store knowledge and recent conversation context.
Do not invent policies, dates, order status, discounts, or timelines.
If the answer is unknown, order-specific, or sensitive, recommend human support.
Keep replies under 120 words.
Ask one clarifying question only when the known policy requires it."""


@dataclass(frozen=True)
class LlmResult:
    reply: str
    metadata: dict = field(default_factory=dict)


class LlmProvider(Protocol):
    async def generate(
        self,
        user_message: str,
        knowledge_items: list[KnowledgeItem],
        history: list[Message],
    ) -> LlmResult:
        ...


class LlmService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key) if self.settings.openai_api_key else None

    async def generate(
        self,
        user_message: str,
        knowledge_items: list[KnowledgeItem],
        history: list[Message],
    ) -> LlmResult:
        started = time.monotonic()
        if self._needs_handoff(user_message) or not knowledge_items:
            return self._handoff_result("unknown_or_sensitive", started)

        if not self.client:
            return self._deterministic_result(knowledge_items, started)

        try:
            return await asyncio.wait_for(
                self._openai_response(user_message, knowledge_items, history, started),
                timeout=self.settings.llm_timeout_seconds,
            )
        except Exception:
            return self._fallback_result(knowledge_items, "llm_error", started)

    async def _openai_response(
        self,
        user_message: str,
        knowledge_items: list[KnowledgeItem],
        history: list[Message],
        started: float,
    ) -> LlmResult:
        assert self.client is not None
        knowledge = "\n".join(f"- {item.title}: {item.content}" for item in knowledge_items)
        recent = [
            {"role": "assistant" if message.sender == "ai" else "user", "content": message.text}
            for message in history
        ]
        completion = await self.client.chat.completions.create(
            model=self.settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "system", "content": f"Store knowledge:\n{knowledge}"},
                *recent,
                {"role": "user", "content": user_message},
            ],
            max_tokens=self.settings.max_output_tokens,
            temperature=0.2,
        )
        reply = completion.choices[0].message.content or HANDOFF_REPLY
        return LlmResult(
            reply=reply.strip(),
            metadata={
                "provider": "openai",
                "model": self.settings.openai_model,
                "latencyMs": round((time.monotonic() - started) * 1000),
                "estimatedTokens": estimate_tokens(user_message) + estimate_tokens(reply),
            },
        )

    def _deterministic_result(self, knowledge_items: list[KnowledgeItem], started: float) -> LlmResult:
        joined = " ".join(item.content for item in knowledge_items)
        reply = joined[:550].strip()
        return LlmResult(
            reply=reply,
            metadata={
                "provider": "faq_fallback",
                "latencyMs": round((time.monotonic() - started) * 1000),
                "estimatedTokens": estimate_tokens(reply),
            },
        )

    def _fallback_result(self, knowledge_items: list[KnowledgeItem], reason: str, started: float) -> LlmResult:
        result = self._deterministic_result(knowledge_items, started)
        return LlmResult(reply=result.reply, metadata={**result.metadata, "fallbackReason": reason})

    def _handoff_result(self, reason: str, started: float) -> LlmResult:
        return LlmResult(
            reply=HANDOFF_REPLY,
            metadata={
                "needsHumanHandoff": True,
                "reason": reason,
                "latencyMs": round((time.monotonic() - started) * 1000),
                "estimatedTokens": estimate_tokens(HANDOFF_REPLY),
            },
        )

    def _needs_handoff(self, message: str) -> bool:
        lower = message.lower()
        return any(term in lower for term in SENSITIVE_OR_ORDER_TERMS)
