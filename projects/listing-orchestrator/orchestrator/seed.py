"""Load seed inventory folders produced by Cozy /studio/ingest or demo_seed."""

from __future__ import annotations

import json
from pathlib import Path

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# Lower sort key = earlier in Etsy / site carousel (graphic first).
ROLE_RANK = {
    "hero_graphic": 0,
    "hero": 0,
    "product": 10,
    "tag": 20,
    "detail": 30,
    "flaw": 40,
    "other": 50,
}


def discover_sku_dirs(seed_root: Path) -> list[Path]:
    if not seed_root.exists():
        return []
    dirs = [p for p in sorted(seed_root.iterdir()) if p.is_dir() and not p.name.startswith(".")]
    if not dirs:
        images = [p for p in seed_root.iterdir() if p.suffix.lower() in IMAGE_EXTS]
        if images:
            return [seed_root]
    return dirs


def _infer_role(filename: str) -> str:
    stem = Path(filename).stem.lower()
    if stem.startswith("hero") or "graphic" in stem:
        return "hero_graphic"
    if "tag" in stem:
        return "tag"
    if "detail" in stem or "close" in stem:
        return "detail"
    if "flaw" in stem or "wear" in stem:
        return "flaw"
    return "product"


def ordered_images(sku_dir: Path, meta: dict) -> tuple[list[Path], list[dict]]:
    """Return images in carousel order + role manifest.

    Prefer ``meta.images``: ``[{"file": "photo_01.jpg", "role": "hero_graphic"}, ...]``.
    Otherwise sort by inferred role, then filename (photo_01 before photo_02).
    """
    manifest = meta.get("images")
    if isinstance(manifest, list) and manifest:
        ordered: list[Path] = []
        roles: list[dict] = []
        for entry in manifest:
            if not isinstance(entry, dict):
                continue
            name = entry.get("file") or entry.get("path")
            if not name:
                continue
            path = sku_dir / str(name)
            if not path.is_file():
                continue
            role = str(entry.get("role") or _infer_role(str(name)))
            ordered.append(path)
            roles.append({"file": path.name, "role": role})
        if ordered:
            return ordered, roles

    files = [p for p in sku_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS]

    def sort_key(p: Path) -> tuple[int, str]:
        role = _infer_role(p.name)
        return (ROLE_RANK.get(role, 50), p.name.lower())

    files = sorted(files, key=sort_key)
    roles = [{"file": p.name, "role": _infer_role(p.name)} for p in files]
    return files, roles


def load_sku_pack(sku_dir: Path) -> tuple[str, list[Path], dict]:
    meta_path = sku_dir / "meta.json"
    meta: dict = {}
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8-sig"))
    sku = str(meta.get("sku") or sku_dir.name)
    images, roles = ordered_images(sku_dir, meta)
    meta = {**meta, "images": roles}
    return sku, images, meta
