"""Channel adapter protocol."""

from __future__ import annotations

from typing import Protocol

from ..models import CanonicalListing, PublishReceipt, SaleEvent


class ChannelAdapter(Protocol):
    name: str

    def publish(self, listing: CanonicalListing) -> PublishReceipt: ...

    def recent_sales(self, limit: int = 20) -> list[SaleEvent]: ...
