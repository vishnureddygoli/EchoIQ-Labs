from typing import Any
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from app.core.config import get_settings
from app.schemas.lead import LeadCreate, LeadResponse
from app.services.lead_service import create_lead

router = APIRouter()

META_FIELD_ALIASES = {
    "full_name": "name",
    "name": "name",
    "phone_number": "phone",
    "phone": "phone",
    "email": "email",
    "city": "city",
    "state": "state",
    "country": "country",
}

def _flatten_meta_field_data(payload: dict[str, Any]) -> dict[str, Any]:
    lead: dict[str, Any] = {}
    entries = payload.get("entry", []) if isinstance(payload, dict) else []
    for entry in entries:
        for change in entry.get("changes", []):
            value = change.get("value", {})
            lead.setdefault("form_id", value.get("form_id"))
            lead.setdefault("ad_id", value.get("ad_id"))
            for field in value.get("field_data", []) or []:
                name = META_FIELD_ALIASES.get(str(field.get("name", "")).lower())
                values = field.get("values") or []
                if name and values:
                    lead[name] = values[0]
    return {k: v for k, v in lead.items() if v is not None}

def _lead_from_payload(payload: dict[str, Any], source: str) -> LeadCreate:
    data = _flatten_meta_field_data(payload) if source == "meta" else {}
    data.update({k: v for k, v in payload.items() if k != "entry"})
    data.setdefault("source_platform", source)
    data.setdefault("raw_payload", payload)
    return LeadCreate(**data)

@router.get("/webhooks/meta", response_class=PlainTextResponse)
def verify_meta(hub_mode: str = Query(alias="hub.mode"), hub_verify_token: str = Query(alias="hub.verify_token"), hub_challenge: str = Query(alias="hub.challenge")):
    if hub_mode == "subscribe" and hub_verify_token == get_settings().meta_verify_token:
        return hub_challenge
    raise HTTPException(status_code=403, detail="invalid verify token")

@router.post("/webhooks/meta", response_model=LeadResponse)
async def meta_webhook(request: Request):
    payload = await request.json()
    return create_lead(_lead_from_payload(payload, "meta"))

@router.post("/webhooks/website", response_model=LeadResponse)
async def website_webhook(request: Request):
    payload = await request.json()
    return create_lead(_lead_from_payload(payload, "website"))

@router.post("/webhooks/whatsapp")
async def whatsapp_placeholder(request: Request):
    payload = await request.json()
    return {"status": "placeholder", "message": "WhatsApp integration is planned for Sprint 2", "received": bool(payload)}
