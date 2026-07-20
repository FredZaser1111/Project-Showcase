"""Load seed inventory folders produced by Cozy /studio/ingest or demo_seed."""

from __future__ import annotations

import json
from pathlib import Path

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def discover_sku_dirs(seed_root: Path) -> list[Path]:
    if not seed_root.exists():
        return []
    dirs = [p for p in sorted(seed_root.iterdir()) if p.is_dir() and not p.name.startswith(".")]
    # Also allow a flat folder of images as a single SKU
    if not dirs:
        images = [p for p in seed_root.iterdir() if p.suffix.lower() in IMAGE_EXTS]
        if images:
            return [seed_root]
    return dirs


def load_sku_pack(sku_dir: Path) -> tuple[str, list[Path], dict]:
    meta_path = sku_dir / "meta.json"
    meta: dict = {}
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    sku = str(meta.get("sku") or sku_dir.name)
    images = sorted(
        p for p in sku_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    )
    return sku, images, meta
