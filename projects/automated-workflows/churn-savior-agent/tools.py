"""Mock Salesforce CRM lookups for the churn agent."""

from __future__ import annotations

from typing import Any

import pandas as pd


def crm_lookup(row: pd.Series) -> dict[str, Any]:
    """Simulate Salesforce Account + Contact fields from local CSV row."""
    return {
        "customer_id": str(row["customer_id"]),
        "company_name": str(row["company_name"]),
        "industry": str(row["industry"]),
        "company_size": str(row["company_size"]),
        "account_manager": str(row["account_manager"]),
        "source": "salesforce_mock_api",
    }
