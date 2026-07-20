"""Canonical listing models for the multi-channel orchestrator."""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

Channel = Literal["shopify", "ebay", "etsy"]
Condition = Literal["New", "Like New", "Lightly Used", "Used"]


class VisionAttributes(BaseModel):
    brand: str = "Unknown"
    category: str = "tops"
    color: str = "unknown"
    garment_type: str = "apparel"
    condition_guess: Condition = "Lightly Used"
    visible_text: list[str] = Field(default_factory=list)
    style_tags: list[str] = Field(default_factory=list)
    confidence: float = 0.5
    notes: str = ""


class CanonicalListing(BaseModel):
    sku: str
    title: str
    description: str
    brand: str
    category: str
    condition: Condition
    price: float
    size: str
    tags: list[str] = Field(default_factory=list)
    authenticity_note: str = (
        "Independent reseller — not affiliated with the brands carried. Authenticity reviewed in-house."
    )
    image_paths: list[str] = Field(default_factory=list)
    vision: Optional[VisionAttributes] = None
    channel_overrides: dict[str, dict[str, Any]] = Field(default_factory=dict)
    source_dir: str = ""


class PublishReceipt(BaseModel):
    sku: str
    channel: Channel
    mode: Literal["live", "mock"]
    external_id: str
    url: Optional[str] = None
    status: str = "published"
    detail: dict[str, Any] = Field(default_factory=dict)


class SaleEvent(BaseModel):
    sale_id: str
    channel: Channel
    sku: str
    title: str
    price: float
    buyer_email: Optional[str] = None
    buyer_name: Optional[str] = None
    marketing_consent: bool = False
    sold_at: str
