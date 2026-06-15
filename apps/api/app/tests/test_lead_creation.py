from uuid import uuid4
from app.schemas.lead import LeadCreate
from app.services import lead_service

class FakeCursor:
    def __init__(self):
        self.last = None
    def execute(self, query, params=None):
        self.last = query
    def fetchone(self):
        if "clients" in self.last:
            return {"id": uuid4()}
        return {"id": uuid4()}
    def __enter__(self): return self
    def __exit__(self, *args): pass

class FakeConn:
    def cursor(self): return FakeCursor()
    def commit(self): pass
    def __enter__(self): return self
    def __exit__(self, *args): pass


def test_lead_creation_with_mock_queue(monkeypatch):
    queued = []
    monkeypatch.setattr(lead_service, "get_connection", lambda: FakeConn())
    monkeypatch.setattr(lead_service, "detect_duplicate", lambda phone, client_id: "new")
    monkeypatch.setattr(lead_service, "enqueue_call", lambda payload: queued.append(payload) or 1)
    response = lead_service.create_lead(LeadCreate(name="John", phone="5125550123", source_platform="website", consent_status="provided"))
    assert response.score == 10
    assert response.queued is True
    assert queued[0]["phone"] == "+15125550123"
