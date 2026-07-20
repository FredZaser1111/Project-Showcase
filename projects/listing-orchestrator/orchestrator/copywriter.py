"""Generate marketplace listing title/description in Cozy Connoisseur voice."""

from __future__ import annotations

import os

from .models import VisionAttributes

VOICE = (
    "Independent authenticated streetwear reseller. Concise, confident, no hype slang overload. "
    "Never claim brand affiliation. Mention condition and authenticity review."
)


def mock_copy(sku: str, vision: VisionAttributes, meta: dict | None = None) -> tuple[str, str, list[str]]:
    meta = meta or {}
    size = meta.get("size") or "One Size"
    brand = vision.brand
    gtype = vision.garment_type
    title = meta.get("title") or f"{brand} {gtype.title()} - {vision.color} · {size}"
    if len(title) > 80:
        title = title[:77] + "..."
    description = meta.get("description") or (
        f"{brand} {gtype} in {vision.color}. Condition: {vision.condition_guess}. "
        f"Size {size}. Photographed in-house. Authenticity reviewed by Cozy Connoisseur Co. "
        f"Independent reseller - not affiliated with {brand}. Ships carefully packed.\n\n"
        f"Tags: {', '.join(vision.style_tags[:6])}."
    )
    tags = list(dict.fromkeys([*vision.style_tags, vision.category, vision.condition_guess.lower()]))
    return title, description, tags


def write_listing_copy(
    sku: str, vision: VisionAttributes, meta: dict | None = None
) -> tuple[str, str, list[str]]:
    meta = meta or {}
    if not os.getenv("OPENAI_API_KEY"):
        return mock_copy(sku, vision, meta)

    try:
        from openai import OpenAI

        client = OpenAI()
        prompt = (
            f"{VOICE}\nSKU={sku}\nVision={vision.model_dump_json()}\nMeta={meta}\n"
            "Return JSON with title, description, tags (array)."
        )
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You write reseller listing copy. JSON only."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
        )
        import json

        data = json.loads(resp.choices[0].message.content or "{}")
        title = data.get("title") or mock_copy(sku, vision, meta)[0]
        description = data.get("description") or mock_copy(sku, vision, meta)[1]
        tags = data.get("tags") or mock_copy(sku, vision, meta)[2]
        return title, description, list(tags)
    except Exception:  # noqa: BLE001
        return mock_copy(sku, vision, meta)
