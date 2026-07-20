"""Shared helpers for Automated Workflows demos (LLM adapter, schemas, thresholds)."""

from .llm import complete
from .thresholds import CHURN_HIGH_RISK, FAILURE_DAYS_THRESHOLD, LOAN_GRAY_HIGH, LOAN_GRAY_LOW

__all__ = [
    "complete",
    "CHURN_HIGH_RISK",
    "FAILURE_DAYS_THRESHOLD",
    "LOAN_GRAY_HIGH",
    "LOAN_GRAY_LOW",
]
