from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class LeadCreate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    country: str | None = None
    region: str | None = None
    state: str | None = None
    city: str | None = None
    language_preference: str | None = "en"
    source_platform: str = "manual"
    campaign_name: str | None = None
    ad_id: str | None = None
    form_id: str | None = None
    landing_page_url: str | None = None
    offer_name: str | None = None
    consent_status: str | None = "provided"
    opt_out_status: bool = False
    raw_payload: dict[str, Any] = Field(default_factory=dict)

class LeadResponse(BaseModel):
    lead_id: UUID
    call_attempt_id: UUID | None = None
    duplicate_status: str
    compliance_status: str
    compliance_reason: str | None = None
    score: int
    lead_temperature: str
    queued: bool = False

class LeadRead(BaseModel):
    id: UUID
    name: str | None
    phone: str
    email: str | None
    country: str | None
    city: str | None
    language_preference: str | None
    source_platform: str
    duplicate_status: str
    compliance_status: str
    created_at: datetime
    score: int | None = None
    lead_temperature: str | None = None

class MetricsSummary(BaseModel):
    total_leads: int
    queued_calls: int
    hot_leads: int
    new_leads: int
    recent_leads: list[LeadRead]
