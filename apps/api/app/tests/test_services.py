from uuid import uuid4
from app.schemas.lead import LeadCreate
from app.services.compliance_service import check_compliance
from app.services.duplicate_service import detect_duplicate
from app.services.normalization_service import detect_country_from_phone, normalize_country, normalize_language, normalize_phone, validate_source_platform
from app.services.scoring_service import initial_score


def test_phone_normalization_and_country_detection():
    assert normalize_phone("(512) 555-0123") == "+15125550123"
    assert normalize_phone("+91 98765 43210") == "+919876543210"
    assert detect_country_from_phone("+919876543210") == "IN"
    assert normalize_phone("123") is None


def test_language_normalization():
    assert normalize_language("english") == "en"
    assert normalize_language("Telugu") == "te"
    assert normalize_language("hindi") == "hi"
    assert normalize_country("USA") == "US"
    assert validate_source_platform("facebook") == "meta"


def test_compliance_blocking():
    assert check_compliance(LeadCreate(phone=None))[0] is False
    assert check_compliance(LeadCreate(phone="+15125550123", consent_status="opted_out"))[1] == "consent_opted_out"
    assert check_compliance(LeadCreate(phone="+15125550123", raw_payload={"note": "do_not_contact"}))[1] == "do_not_contact"


def test_initial_scoring():
    assert initial_score(False, "do_not_contact", "new")[:2] == (0, "do_not_contact")
    assert initial_score(True, None, "new")[:2] == (10, "new")
    assert initial_score(True, None, "possible_duplicate")[:2] == (5, "new")


def test_duplicate_detection_new(monkeypatch):
    monkeypatch.setattr("app.services.duplicate_service.fetch_one", lambda *args, **kwargs: None)
    assert detect_duplicate("+15125550123", uuid4()) == "new"


def test_duplicate_detection_exact(monkeypatch):
    monkeypatch.setattr("app.services.duplicate_service.fetch_one", lambda *args, **kwargs: {"id": uuid4()})
    assert detect_duplicate("+15125550123", uuid4()) == "duplicate"
