from .ebay import EbayAdapter
from .etsy import EtsyAdapter
from .shopify import ShopifyAdapter

__all__ = ["ShopifyAdapter", "EbayAdapter", "EtsyAdapter"]


def get_adapters(channels: list[str] | None = None):
    mapping = {
        "shopify": ShopifyAdapter,
        "ebay": EbayAdapter,
        "etsy": EtsyAdapter,
    }
    selected = channels or ["shopify", "ebay", "etsy"]
    return [mapping[name]() for name in selected if name in mapping]
