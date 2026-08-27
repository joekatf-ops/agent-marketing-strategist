"""Central secret detection and whole-field redaction for portable artifacts."""

from __future__ import annotations

import re


REDACTED = "[REDACTED]"

_CREDENTIAL_FINGERPRINT = re.compile(
    r"(?<![A-Za-z0-9])(?:"
    r"gh[pousr]_[A-Za-z0-9]{36,255}|"
    r"github_pat_[A-Za-z0-9_]{60,255}|"
    r"glpat-[A-Za-z0-9_-]{20,255}|"
    r"npm_[A-Za-z0-9]{36}|"
    r"(?:AKIA|ASIA)[A-Z0-9]{16}|"
    r"AIza[0-9A-Za-z_-]{35}|"
    r"xox[baprs]-[0-9A-Za-z-]{20,255}|"
    r"sk_live_[0-9A-Za-z]{20,255}|"
    r"sk-(?:proj-)?[0-9A-Za-z_-]{20,255}|"
    r"sk-ant-[0-9A-Za-z_-]{20,255}"
    r")(?![A-Za-z0-9])"
)
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)(?<![A-Za-z0-9])['\"]?[A-Za-z0-9_.-]*(?:"
    r"api[_-]?key|access[_-]?token|refresh[_-]?token|session[_-]?token|"
    r"client[_-]?secret|secret[_-]?access[_-]?key|private[_-]?key|"
    r"password|passwd|credential|secret|token"
    r")[\"']?\s*[:=]\s*[^\s,}\]]+"
)
_AUTHORIZATION_VALUE = re.compile(
    r"(?i)\bauthorization\s*[:=]\s*(?:bearer|basic)\s+\S+"
)
_BEARER_VALUE = re.compile(
    r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{4,}"
)
_PRIVATE_KEY_BLOCK = re.compile(
    r"-----BEGIN (?P<kind>(?:ENCRYPTED |RSA |EC |DSA |OPENSSH )?PRIVATE KEY)-----"
    r".*?-----END (?P=kind)-----",
    re.DOTALL,
)
_PRIVATE_KEY_HEADER = re.compile(
    r"-----BEGIN (?:ENCRYPTED |RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
)
_URL = re.compile(r"(?i)\b[A-Za-z][A-Za-z0-9+.-]*://[^\s<>\"']+")
_PERCENT_ESCAPE = re.compile(r"%([0-9A-Fa-f]{2})")
_SENSITIVE_KEY_SUFFIXES = (
    "apikey",
    "accesstoken",
    "refreshtoken",
    "sessiontoken",
    "clientsecret",
    "privatekey",
    "password",
    "passwd",
    "authorization",
    "secretaccesskey",
    "accesskeyid",
    "credential",
    "credentials",
    "secret",
    "token",
)


def normalized_key(value: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def sensitive_key(value: object) -> bool:
    name = normalized_key(value)
    return bool(name) and name.endswith(_SENSITIVE_KEY_SUFFIXES)


def _decode_url_component(value: str) -> str:
    return _PERCENT_ESCAPE.sub(
        lambda match: chr(int(match.group(1), 16)), value.replace("+", " ")
    )


def _url_contains_secret(value: str) -> bool:
    for match in _URL.finditer(value):
        url = match.group(0)
        remainder = url.split("://", 1)[1]
        authority = re.split(r"[/#?]", remainder, 1)[0]
        if "@" in authority:
            return True
        if "?" not in remainder:
            continue
        query = remainder.split("?", 1)[1].split("#", 1)[0]
        for field in query.split("&"):
            key, separator, field_value = field.partition("=")
            if not separator:
                continue
            if sensitive_key(_decode_url_component(key)) and _decode_url_component(
                field_value
            ) not in {"", "null"}:
                return True
    return False


def text_contains_secret(value: str) -> bool:
    return bool(
        _CREDENTIAL_FINGERPRINT.search(value)
        or _SECRET_ASSIGNMENT.search(value)
        or _AUTHORIZATION_VALUE.search(value)
        or _BEARER_VALUE.search(value)
        or _PRIVATE_KEY_BLOCK.search(value)
        or _PRIVATE_KEY_HEADER.search(value)
        or _url_contains_secret(value)
    )


def _meaningful_secret_value(value: object) -> bool:
    return value not in (None, "", False)


def sanitize_structure(
    value: object, path: str = ""
) -> tuple[object, tuple[str, ...]]:
    """Return a deep safe copy and every field path that was wholly redacted."""
    if isinstance(value, str):
        if text_contains_secret(value):
            return REDACTED, (path or "intake",)
        return value, ()
    if isinstance(value, list):
        safe_items: list[object] = []
        findings: list[str] = []
        for index, item in enumerate(value):
            child = f"{path}[{index}]" if path else f"[{index}]"
            safe_item, nested = sanitize_structure(item, child)
            safe_items.append(safe_item)
            findings.extend(nested)
        return safe_items, tuple(findings)
    if isinstance(value, dict):
        safe_mapping: dict[object, object] = {}
        findings = []
        for key, item in value.items():
            safe_key: object = key
            if isinstance(key, str) and text_contains_secret(key):
                safe_key = "[REDACTED_KEY]"
                findings.append(f"{path or 'intake'} key")
            child = f"{path}.{key}" if path else str(key)
            if isinstance(key, str) and sensitive_key(key) and _meaningful_secret_value(item):
                safe_mapping[safe_key] = REDACTED
                findings.append(child)
                continue
            safe_item, nested = sanitize_structure(item, child)
            safe_mapping[safe_key] = safe_item
            findings.extend(nested)
        return safe_mapping, tuple(findings)
    return value, ()


def structure_contains_secret(value: object) -> bool:
    _safe, findings = sanitize_structure(value)
    return bool(findings)


def redact_text(value: str) -> str:
    """Redact the entire supplied field when any supported secret form appears."""
    return REDACTED if text_contains_secret(value) else value
