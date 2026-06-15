from fastapi.testclient import TestClient
from app.api.routes import webhooks
from app.main import app
from app.schemas.lead import LeadResponse

client = TestClient(app)


def test_meta_verification_returns_plain_challenge():
    response = client.get("/webhooks/meta", params={"hub.mode": "subscribe", "hub.verify_token": "dev-meta-token", "hub.challenge": "12345"})
    assert response.status_code == 200
    assert response.text == "12345"


def test_meta_payload_flattening():
    payload = {
        "entry": [{"changes": [{"value": {"form_id": "form-1", "ad_id": "ad-1", "field_data": [
            {"name": "full_name", "values": ["Jane Lead"]},
            {"name": "phone_number", "values": ["+15125550199"]},
            {"name": "email", "values": ["jane@example.com"]},
        ]}}]}]
    }
    lead = webhooks._lead_from_payload(payload, "meta")
    assert lead.name == "Jane Lead"
    assert lead.phone == "+15125550199"
    assert lead.email == "jane@example.com"
    assert lead.form_id == "form-1"
    assert lead.ad_id == "ad-1"
    assert lead.source_platform == "meta"


def test_website_webhook_routes_to_lead_service(monkeypatch):
    def fake_create_lead(lead):
        assert lead.source_platform == "website"
        assert lead.raw_payload["phone"] == "+15125550123"
        return LeadResponse(lead_id="00000000-0000-0000-0000-000000000001", call_attempt_id=None, duplicate_status="new", compliance_status="callable", score=10, lead_temperature="new", queued=False)

    monkeypatch.setattr(webhooks, "create_lead", fake_create_lead)
    response = client.post("/webhooks/website", json={"name": "John", "phone": "+15125550123"})
    assert response.status_code == 200
    assert response.json()["lead_id"] == "00000000-0000-0000-0000-000000000001"
