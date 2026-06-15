from typing import Any
from uuid import UUID
from app.core.config import get_settings
from app.core.database import get_connection, fetch_all, fetch_one
from app.core.redis_client import enqueue_call
from app.schemas.lead import LeadCreate, LeadResponse
from app.services.call_dispatch_service import create_call_payload
from app.services.compliance_service import check_compliance
from app.services.duplicate_service import detect_duplicate
from app.services.normalization_service import detect_country_from_phone, normalize_language, normalize_phone, validate_source_platform
from app.services.scoring_service import initial_score


def _default_client_id(conn) -> UUID:
    settings = get_settings()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO clients (name, country, timezone) VALUES (%s, %s, %s)
            ON CONFLICT (name) DO UPDATE SET country = EXCLUDED.country
            RETURNING id
            """,
            (settings.default_client_name, settings.default_client_country, settings.default_client_timezone),
        )
        return cur.fetchone()["id"]

def create_lead(payload: LeadCreate) -> LeadResponse:
    phone = normalize_phone(payload.phone)
    source = validate_source_platform(payload.source_platform)
    language = normalize_language(payload.language_preference)
    country = payload.country or detect_country_from_phone(phone)
    normalized = payload.model_copy(update={"phone": phone, "source_platform": source, "language_preference": language, "country": country})
    is_compliant, compliance_reason = check_compliance(normalized)
    compliance_status = "callable" if is_compliant else "blocked"
    call_attempt_id = None
    queued = False
    with get_connection() as conn:
        client_id = _default_client_id(conn)
        duplicate_status = detect_duplicate(phone or "", client_id) if phone else "new"
        is_callable = is_compliant and duplicate_status != "duplicate"
        score, temperature, score_reason = initial_score(is_callable, compliance_reason, duplicate_status)
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO leads (client_id, name, phone, email, country, region, state, city, language_preference,
                  source_platform, campaign_name, ad_id, form_id, landing_page_url, offer_name, consent_status,
                  opt_out_status, duplicate_status, compliance_status, compliance_reason, raw_payload)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id
                """,
                (client_id, normalized.name, normalized.phone or "", normalized.email, normalized.country, normalized.region,
                 normalized.state, normalized.city, normalized.language_preference, normalized.source_platform,
                 normalized.campaign_name, normalized.ad_id, normalized.form_id, normalized.landing_page_url,
                 normalized.offer_name, normalized.consent_status, normalized.opt_out_status, duplicate_status,
                 compliance_status, compliance_reason, normalized.raw_payload),
            )
            lead_id = cur.fetchone()["id"]
            cur.execute("INSERT INTO lead_scores (lead_id, score, lead_temperature, reason) VALUES (%s,%s,%s,%s)", (lead_id, score, temperature, score_reason))
            if is_callable:
                cur.execute("INSERT INTO call_attempts (lead_id, call_status, target_call_seconds) VALUES (%s, 'queued', 10) RETURNING id", (lead_id,))
                call_attempt_id = cur.fetchone()["id"]
        conn.commit()
    if call_attempt_id and get_settings().mock_calling_enabled:
        enqueue_call(create_call_payload(lead_id=lead_id, call_attempt_id=call_attempt_id, phone=phone or "", language=language, country=country, source=source))
        queued = True
    return LeadResponse(lead_id=lead_id, call_attempt_id=call_attempt_id, duplicate_status=duplicate_status, compliance_status=compliance_status, compliance_reason=compliance_reason, score=score, lead_temperature=temperature, queued=queued)

def list_leads(limit: int = 50) -> list[dict[str, Any]]:
    return fetch_all("""
      SELECT l.id,l.name,l.phone,l.email,l.country,l.city,l.language_preference,l.source_platform,l.duplicate_status,l.compliance_status,l.created_at,
             s.score,s.lead_temperature
      FROM leads l LEFT JOIN LATERAL (SELECT score, lead_temperature FROM lead_scores WHERE lead_id=l.id ORDER BY created_at DESC LIMIT 1) s ON true
      ORDER BY l.created_at DESC LIMIT %s
    """, (limit,))

def get_lead(lead_id: UUID) -> dict[str, Any] | None:
    return fetch_one("SELECT * FROM leads WHERE id=%s", (lead_id,))

def metrics_summary() -> dict[str, Any]:
    total = fetch_one("SELECT count(*) AS c FROM leads")["c"]
    queued = fetch_one("SELECT count(*) AS c FROM call_attempts WHERE call_status='queued'")["c"]
    hot = fetch_one("SELECT count(*) AS c FROM lead_scores WHERE score >= 10")["c"]
    new = fetch_one("SELECT count(*) AS c FROM leads WHERE duplicate_status='new'")["c"]
    return {"total_leads": total, "queued_calls": queued, "hot_leads": hot, "new_leads": new, "recent_leads": list_leads(10)}
