from uuid import UUID
from fastapi import APIRouter, HTTPException
from app.schemas.lead import LeadCreate, LeadRead, LeadResponse, MetricsSummary
from app.services.lead_service import create_lead, get_lead, list_leads, metrics_summary

router = APIRouter()

@router.post("/leads", response_model=LeadResponse)
def post_lead(lead: LeadCreate):
    try:
        return create_lead(lead)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.get("/leads", response_model=list[LeadRead])
def get_leads(limit: int = 50):
    return list_leads(limit)

@router.get("/leads/metrics/summary", response_model=MetricsSummary)
def get_summary():
    return metrics_summary()

@router.get("/leads/{lead_id}")
def get_one_lead(lead_id: UUID):
    lead = get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="lead not found")
    return lead
