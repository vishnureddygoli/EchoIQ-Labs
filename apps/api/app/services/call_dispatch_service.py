from datetime import datetime, timezone
from uuid import UUID

def create_call_payload(*, lead_id: UUID, call_attempt_id: UUID, phone: str, language: str, country: str | None, source: str) -> dict[str, str | int]:
    return {
        "lead_id": str(lead_id),
        "call_attempt_id": str(call_attempt_id),
        "phone": phone,
        "language": language,
        "country": country or "",
        "source": source,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "target_call_seconds": 10,
    }
