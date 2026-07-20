"""Vision enrichment — OpenAI when keyed, else deterministic mock from filename/meta."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from .models import Condition, VisionAttributes

BRAND_HINTS = {
    "supreme": "Supreme",
    "nike": "Nike",
    "adidas": "Adidas",
    "denim": "Denim Tears",
    "stussy": "Stüssy",
    "carhartt": "Carhartt",
    "palace": "Palace",
    "bape": "BAPE",
}


def _guess_brand(text: str) -> str:
    lower = text.lower()
    for key, brand in BRAND_HINTS.items():
        if key in lower:
            return brand
    return "Unknown"


def _guess_category(text: str) -> str:
    lower = text.lower()
    if any(w in lower for w in ("hat", "cap", "beanie")):
        return "hats"
    if any(w in lower for w in ("jean", "pant", "short", "bottom")):
        return "bottoms"
    if any(w in lower for w in ("hoodie", "tee", "shirt", "crew", "top", "jacket")):
        return "tops"
    return "accessories"


def mock_vision(image_paths: list[Path], meta: dict | None = None) -> VisionAttributes:
    meta = meta or {}
    blob = " ".join([*(p.stem for p in image_paths), json.dumps(meta)])
    brand = meta.get("brand") or _guess_brand(blob)
    category = meta.get("category") or _guess_category(blob)
    condition: Condition = meta.get("condition") or "Lightly Used"
    color = meta.get("color") or "multi"
    tags = list(meta.get("style_tags") or [])
    if brand != "Unknown" and brand.lower() not in {t.lower() for t in tags}:
        tags.append(brand)
    tags.extend(["streetwear", "authenticated-reseller"])
    return VisionAttributes(
        brand=brand,
        category=category,
        color=color,
        garment_type=meta.get("garment_type") or category.rstrip("s"),
        condition_guess=condition,
        visible_text=re.findall(r"[A-Za-z]{3,}", blob)[:8],
        style_tags=sorted(set(tags)),
        confidence=0.72 if brand != "Unknown" else 0.45,
        notes="Mock vision from filename/meta (set OPENAI_API_KEY for live vision).",
    )


def enrich_vision(image_paths: list[Path], meta: dict | None = None) -> VisionAttributes:
    meta = meta or {}
    if not os.getenv("OPENAI_API_KEY"):
        return mock_vision(image_paths, meta)

    try:
        import base64

        from openai import OpenAI

        client = OpenAI()
        content: list[dict] = [
            {
                "type": "text",
                "text": (
                    "You catalog streetwear for a reseller. Return JSON with keys: "
                    "brand, category (hats|bottoms|tops|accessories), color, garment_type, "
                    "condition_guess (New|Like New|Lightly Used|Used), visible_text (array), "
                    "style_tags (array), confidence (0-1), notes."
                ),
            }
        ]
        for path in image_paths[:4]:
            raw = path.read_bytes()
            b64 = base64.standard_b64encode(raw).decode("ascii")
            mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{b64}"},
                }
            )
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": content}],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        data = json.loads(resp.choices[0].message.content or "{}")
        # Prefer explicit meta overrides
        for key in ("brand", "category", "condition", "color"):
            if meta.get(key):
                data["condition_guess" if key == "condition" else key] = meta[key]
        return VisionAttributes(**{**mock_vision(image_paths, meta).model_dump(), **data})
    except Exception as exc:  # noqa: BLE001
        attrs = mock_vision(image_paths, meta)
        attrs.notes = f"Vision fallback to mock ({exc})"
        return attrs
