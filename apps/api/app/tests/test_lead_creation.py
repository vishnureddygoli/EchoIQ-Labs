from uuid import uuid4
from app.schemas.lead import LeadCreate
from app.services import lead_service

class FakeCursor:
    def __init__(self, call_attempt_id):
        self.last = ""
        self.call_attempt_id = call_attempt_id
        self.params = []
    def execute(self, query, params=None):
        self.last = query
        self.params.append(params)
    def fetchone(self):
        if "INSERT INTO clients" in self.last:
            return {"id": uuid4()}
        if "INSERT INTO leads" in self.last:
            return {"id": uuid4()}
        if "INSERT INTO call_attempts" in self.last:
            return {"id": self.call_attempt_id}
        return {"id": uuid4()}
    def __enter__(self): return self
    def __exit__(self, *args): pass

class FakeConn:
    def __init__(self, call_attempt_id):
        self.call_attempt_id = call_attempt_id
    def cursor(self): return FakeCursor(self.call_attempt_id)
    def commit(self): pass
    def __enter__(self): return self
    def __exit__(self, *args): pass


def test_lead_creation_with_mock_queue(monkeypatch):
    queued = []
    call_attempt_id = uuid4()
    monkeypatch.setattr(lead_service, "get_connection", lambda: FakeConn(call_attempt_id))
    monkeypatch.setattr(lead_service, "detect_duplicate", lambda phone, client_id: "new")
    monkeypatch.setattr(lead_service, "enqueue_call", lambda payload: queued.append(payload) or 1)

    response = lead_service.create_lead(LeadCreate(name="John", phone="5125550123", country="USA", source_platform="website", consent_status="provided"))

    assert response.lead_id is not None
    assert response.call_attempt_id == call_attempt_id
    assert response.score == 10
    assert response.queued is True
    assert len(queued) == 1
    assert queued[0] == {
        "lead_id": str(response.lead_id),
        "call_attempt_id": str(response.call_attempt_id),
        "phone": "+15125550123",
        "language": "en",
        "country": "US",
        "source": "website",
        "created_at": queued[0]["created_at"],
        "target_call_seconds": 10,
    }


def test_duplicate_lead_does_not_create_call_attempt_or_queue(monkeypatch):
    queued = []
    monkeypatch.setattr(lead_service, "get_connection", lambda: FakeConn(uuid4()))
    monkeypatch.setattr(lead_service, "detect_duplicate", lambda phone, client_id: "duplicate")
    monkeypatch.setattr(lead_service, "enqueue_call", lambda payload: queued.append(payload) or 1)

    response = lead_service.create_lead(LeadCreate(name="Dupe", phone="+15125550123", source_platform="manual", consent_status="provided"))

    assert response.duplicate_status == "duplicate"
    assert response.score == 0
    assert response.lead_temperature == "invalid"
    assert response.call_attempt_id is None
    assert response.queued is False
    assert queued == []
