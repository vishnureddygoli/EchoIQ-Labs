from uuid import UUID
from app.core.database import fetch_one

def detect_duplicate(phone: str, client_id: UUID) -> str:
    exact = fetch_one("SELECT id FROM leads WHERE phone = %s AND client_id = %s LIMIT 1", (phone, client_id))
    if exact:
        return "duplicate"
    tail = phone[-10:]
    possible = fetch_one("SELECT id FROM leads WHERE right(phone, 10) = %s AND client_id = %s LIMIT 1", (tail, client_id))
    return "possible_duplicate" if possible else "new"
