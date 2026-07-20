"""Create demo seed packs + run full mock pipeline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from orchestrator.pipeline import run_pipeline  # noqa: E402


def _make_image(path: Path, label: str, color: tuple[int, int, int]) -> None:
    img = Image.new("RGB", (800, 1000), color)
    draw = ImageDraw.Draw(img)
    draw.rectangle((40, 40, 760, 960), outline=(255, 255, 255), width=4)
    draw.text((80, 120), "COZY CONNOISSEUR", fill=(255, 255, 255))
    draw.text((80, 200), label, fill=(255, 255, 255))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="JPEG", quality=90)


def ensure_demo_seed() -> Path:
    seed = ROOT / "data" / "demo_seed"
    packs = [
        {
            "sku": "CCC-SUP-HAT-001",
            "meta": {
                "sku": "CCC-SUP-HAT-001",
                "brand": "Supreme",
                "category": "hats",
                "condition": "New",
                "color": "black",
                "size": "OSFA",
                "price": 148,
                "style_tags": ["supreme", "camp-cap", "streetwear"],
            },
            "color": (20, 20, 20),
            "label": "Supreme Camp Cap",
        },
        {
            "sku": "CCC-DT-JEAN-002",
            "meta": {
                "sku": "CCC-DT-JEAN-002",
                "brand": "Denim Tears",
                "category": "bottoms",
                "condition": "Lightly Used",
                "color": "indigo",
                "size": "32",
                "price": 220,
                "style_tags": ["denim-tears", "jeans"],
            },
            "color": (35, 55, 95),
            "label": "Denim Tears Jeans",
        },
        {
            "sku": "CCC-NK-TEE-003",
            "meta": {
                "sku": "CCC-NK-TEE-003",
                "brand": "Nike",
                "category": "tops",
                "condition": "Like New",
                "color": "cream",
                "size": "L",
                "price": 64,
                "style_tags": ["nike", "tee"],
            },
            "color": (180, 160, 130),
            "label": "Nike Tee",
        },
    ]
    for pack in packs:
        d = seed / pack["sku"]
        _make_image(d / "photo_01.jpg", pack["label"], pack["color"])
        _make_image(d / "photo_02.jpg", pack["label"] + " detail", tuple(min(255, c + 30) for c in pack["color"]))
        (d / "meta.json").write_text(json.dumps(pack["meta"], indent=2), encoding="utf-8")
    return seed


def main() -> None:
    seed = ensure_demo_seed()
    log = run_pipeline(seed, channels=["shopify", "ebay", "etsy"])
    print(json.dumps(log, indent=2))
    print(f"\nDemo complete. See {ROOT / 'outputs'}")


if __name__ == "__main__":
    main()
