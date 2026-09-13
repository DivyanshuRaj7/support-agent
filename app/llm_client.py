"""
LLM client abstraction.

WHY THIS EXISTS (interview talking point):
Agents should never call `openai.chat.completions.create(...)` directly inside
business logic. Wrapping it means:
  1. You can swap providers (OpenAI -> Anthropic -> local model) with one change.
  2. You can mock it for tests/demos without burning API calls or needing a key.
  3. You have one place to add retries, timeouts, and cost logging later.

In demo/no-API-key mode, `MockLLM` returns deterministic keyword-based responses
so the whole graph is runnable and testable end-to-end without secrets.
"""

import os
import re
from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    def classify(self, ticket_text: str) -> str:
        """Return one of: billing, technical, refund, general"""
        ...

    @abstractmethod
    def generate_response(self, category: str, ticket_text: str, tool_context: str) -> str:
        """Draft a customer-facing response given category + tool results."""
        ...


class MockLLM(LLMClient):
    """Deterministic stand-in so the pipeline runs with zero API keys.
    Replace with OpenAILLM in production — this is here so graders / interviewers
    can run `python -m app.main` immediately."""

    KEYWORDS = {
        "billing": ["charge", "invoice", "bill", "payment", "subscription"],
        "refund": ["refund", "money back", "cancel my order", "return"],
        "technical": ["error", "bug", "not working", "crash", "login"],
    }

    def classify(self, ticket_text: str) -> str:
        text = ticket_text.lower()
        for category, keywords in self.KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return category
        return "general"

    def generate_response(self, category: str, ticket_text: str, tool_context: str) -> str:
        return (
            f"[{category.upper()} AGENT] Based on your message and account data "
            f"({tool_context}), here is a draft resolution for: '{ticket_text[:60]}...'"
        )


class OpenAILLM(LLMClient):
    """Production implementation. Requires OPENAI_API_KEY in environment."""

    def __init__(self, model: str = "gpt-4o-mini"):
        from openai import OpenAI
        self.client = OpenAI()
        self.model = model

    def classify(self, ticket_text: str) -> str:
        prompt = (
            "Classify this support ticket into exactly one category: "
            "billing, technical, refund, general.\n"
            f"Ticket: {ticket_text}\nRespond with only the category word."
        )
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        category = resp.choices[0].message.content.strip().lower()
        return category if category in {"billing", "technical", "refund", "general"} else "general"

    def generate_response(self, category: str, ticket_text: str, tool_context: str) -> str:
        prompt = (
            f"You are a {category} support agent. Using this account context: "
            f"{tool_context}\nDraft a helpful, concise reply to: {ticket_text}"
        )
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content


def get_llm_client() -> LLMClient:
    """Factory: uses real OpenAI if a key is present, otherwise falls back to
    MockLLM so the project always runs. This fallback pattern is itself worth
    mentioning in interviews — graceful degradation instead of a hard crash."""
    if os.getenv("OPENAI_API_KEY"):
        try:
            return OpenAILLM()
        except Exception:
            return MockLLM()
    return MockLLM()
