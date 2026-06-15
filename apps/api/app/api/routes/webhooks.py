from typing import Any
from fastapi import APIRouter, HTTPException, Query, Request
from app.core.config import get_settings
from app.schemas.lead import LeadCreate, LeadResponse
from app.services.lead_service import create_lead

router = APIRouter()

def _lead_from_payload(payload: dict[str, Any], source: str) -> LeadCreate:
    data = dict(payload)
    data.setdefault("source_platform", source)
    data.setdefault("raw_payload", payload)
    return LeadCreate(**data)

@router.get("/webhooks/meta")
def verify_meta(hub_mode: str = Query(alias="hub.mode"), hub_verify_token: str = Query(alias="hub.verify_token"), hub_challenge: str = Query(alias="hub.challenge")):
    if hub_mode == "subscribe" and hub_verify_token == get_settings().meta_verify_token:
        return int(hub_challenge) if hub_challenge.isdigit() else hub_challenge
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
