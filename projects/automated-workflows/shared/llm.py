"""Mock-by-default LLM adapter; uses OpenAI or Anthropic when keys are set."""

from __future__ import annotations

import os
from typing import Literal

LlmMode = Literal["mock", "openai", "anthropic"]


def detect_mode() -> LlmMode:
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    return "mock"


def complete(system: str, user: str, *, mock_fallback: str) -> tuple[str, LlmMode]:
    """Return (text, mode). Never raises for missing keys — falls back to mock."""
    mode = detect_mode()
    if mode == "openai":
        try:
            from openai import OpenAI

            client = OpenAI()
            resp = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.3,
            )
            text = (resp.choices[0].message.content or "").strip()
            if text:
                return text, mode
        except Exception as exc:  # noqa: BLE001 — demo resilience
            return f"{mock_fallback}\n\n[openai_fallback: {exc}]", "mock"

    if mode == "anthropic":
        try:
            import anthropic

            client = anthropic.Anthropic()
            resp = client.messages.create(
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest"),
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
            text = "\n".join(parts).strip()
            if text:
                return text, mode
        except Exception as exc:  # noqa: BLE001
            return f"{mock_fallback}\n\n[anthropic_fallback: {exc}]", "mock"

    return mock_fallback, "mock"
