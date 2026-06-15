from app.schemas.lead import LeadCreate

DO_NOT_CONTACT_PHRASES = ("do_not_contact", "do not contact", "don't contact", "dont contact")

def check_compliance(lead: LeadCreate) -> tuple[bool, str | None]:
    if not lead.phone:
        return False, "phone_missing_or_invalid"
    if (lead.consent_status or "").strip().lower() == "opted_out":
        return False, "consent_opted_out"
    if lead.opt_out_status:
        return False, "opt_out_status_true"
    raw_opt_out = lead.raw_payload.get("opt_out_status") if isinstance(lead.raw_payload, dict) else None
    if raw_opt_out is True or str(raw_opt_out).lower() == "true":
        return False, "opt_out_status_true"
    haystack = " ".join(str(v).lower() for v in [lead.name, lead.email, lead.offer_name, lead.campaign_name, lead.raw_payload])
    if any(phrase in haystack for phrase in DO_NOT_CONTACT_PHRASES):
        return False, "do_not_contact"
    return True, None
