import re

SOURCE_PLATFORMS = {"website", "manual", "meta", "whatsapp"}
SOURCE_ALIASES = {"facebook": "meta", "instagram": "meta", "fb": "meta", "ig": "meta", "web": "website"}
LANGUAGE_MAP = {"english": "en", "en": "en", "telugu": "te", "te": "te", "hindi": "hi", "hi": "hi"}
COUNTRY_PREFIXES = {"1": "US", "91": "IN", "44": "GB", "61": "AU"}
COUNTRY_ALIASES = {"usa": "US", "united states": "US", "us": "US", "india": "IN", "in": "IN", "uk": "GB", "gb": "GB", "australia": "AU", "au": "AU"}

def normalize_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    cleaned = re.sub(r"[^\d+]", "", phone.strip())
    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]
    digits = re.sub(r"\D", "", cleaned)
    if not digits or len(digits) < 10 or len(digits) > 15:
        return None
    if cleaned.startswith("+"):
        return "+" + digits
    if len(digits) == 10:
        return "+1" + digits
    return "+" + digits

def detect_country_from_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    for prefix, country in sorted(COUNTRY_PREFIXES.items(), key=lambda i: len(i[0]), reverse=True):
        if digits.startswith(prefix):
            return country
    return None

def normalize_country(value: str | None, phone: str | None = None, default: str | None = None) -> str | None:
    if value:
        key = value.strip().lower()
        return COUNTRY_ALIASES.get(key, value.strip().upper())
    return detect_country_from_phone(phone) or default

def normalize_language(value: str | None) -> str:
    if not value:
        return "en"
    return LANGUAGE_MAP.get(value.strip().lower(), value.strip().lower()[:2] or "en")

def validate_source_platform(value: str | None) -> str:
    source = (value or "manual").strip().lower()
    source = SOURCE_ALIASES.get(source, source)
    if source not in SOURCE_PLATFORMS:
        raise ValueError(f"unsupported source_platform: {source}")
    return source
