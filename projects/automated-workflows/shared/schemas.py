"""Pydantic case-packet shapes shared across workflow demos."""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class CasePacket(BaseModel):
    """Generic envelope for agent outputs recruiters can skim as JSON."""

    project: str
    case_id: str
    score: float
    decision: str
    summary: str
    actions: list[str] = Field(default_factory=list)
    artifacts: dict[str, Any] = Field(default_factory=dict)
    hitl_required: bool = False
    llm_mode: Literal["mock", "openai", "anthropic"] = "mock"


class ChurnCase(CasePacket):
    customer_id: str
    churn_probability: float
    crm_profile: dict[str, Any] = Field(default_factory=dict)
    ticket_analysis: str = ""
    offer_or_escalation: str = ""


class LoanCase(CasePacket):
    application_id: str
    default_risk: float
    route: Literal["auto_approve", "auto_deny", "compliance_review"]
    compliance_report: Optional[str] = None
    webhook_payload: dict[str, Any] = Field(default_factory=dict)


class MaintenanceCase(CasePacket):
    asset_id: str
    days_to_failure: float
    parts_in_stock: bool
    purchase_order: Optional[dict[str, Any]] = None
    approval_queue_id: Optional[str] = None
