def initial_score(is_callable: bool, compliance_reason: str | None, duplicate_status: str) -> tuple[int, str, str | None]:
    if not is_callable:
        temperature = "do_not_contact" if compliance_reason == "do_not_contact" else "invalid"
        reason = compliance_reason or duplicate_status
        return 0, temperature, reason
    if duplicate_status == "possible_duplicate":
        return 5, "new", "possible_duplicate"
    return 10, "new", "valid_new_lead"
