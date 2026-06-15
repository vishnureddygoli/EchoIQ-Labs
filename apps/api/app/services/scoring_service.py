def initial_score(is_callable: bool, compliance_reason: str | None, duplicate_status: str) -> tuple[int, str, str | None]:
    if not is_callable:
        temperature = "do_not_contact" if compliance_reason == "do_not_contact" else "invalid"
        return 0, temperature, compliance_reason
    if duplicate_status == "possible_duplicate":
        return 5, "new", "possible_duplicate"
    if duplicate_status == "duplicate":
        return 0, "invalid", "duplicate"
    return 10, "new", "valid_new_lead"
