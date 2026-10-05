import re
import unicodedata
from collections import Counter
from email.utils import getaddresses
from urllib.parse import urlparse

from app.services.email_parser import ParsedEmail
from app.services.preprocessing import prepare_email


FEATURE_NAMES = (
    "subject_length",
    "body_length",
    "word_count",
    "url_count",
    "unique_url_count",
    "ip_url_count",
    "shortener_url_count",
    "https_url_ratio",
    "email_address_count",
    "sender_reply_to_domain_mismatch",
    "sender_return_path_domain_mismatch",
    "sender_display_name_mismatch",
    "urgency_word_count",
    "credential_word_count",
    "financial_word_count",
    "threat_word_count",
    "exclamation_count",
    "uppercase_ratio",
    "subject_has_reply_prefix",
    "subject_has_urgent_term",
    "subject_has_financial_term",
    "subject_is_empty",
    "body_has_greeting",
    "body_has_signature",
    "html_has_form",
    "html_has_password_input",
    "html_has_iframe",
    "html_has_hidden_element",
    "html_has_script",
    "has_attachment",
    "attachment_count",
    "has_received_header",
    "spf_pass",
    "dkim_pass",
    "dmarc_pass",
    "body_has_control_character",
    "link_text_mismatch_count",
    "url_uses_punycode",
    "sender_uses_free_email",
    "external_url_count",
)

_URL = re.compile(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+", re.IGNORECASE)
_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_IP_HOST = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
_SHORTENERS = {
    "bit.ly", "t.co", "tinyurl.com", "goo.gl", "ow.ly", "is.gd",
    "buff.ly", "cutt.ly", "tiny.cc",
}
_FREE_EMAIL = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "live.com",
    "aol.com", "icloud.com", "proton.me", "protonmail.com",
}
_URGENCY = {"urgent", "immediately", "asap", "today", "now", "action", "expire", "suspend"}
_CREDENTIALS = {"password", "credential", "login", "sign-in", "verify", "account", "authenticate"}
_FINANCIAL = {"payment", "invoice", "bank", "billing", "wire", "refund", "crypto", "wallet"}
_THREATS = {"suspend", "suspended", "terminate", "locked", "close", "penalty", "unauthorized"}
_GREETING = re.compile(r"\b(dear|hello|hi|good morning|good afternoon)\b", re.IGNORECASE)
_SIGNATURE = re.compile(r"\b(regards|sincerely|thank you|best wishes|sent from)\b", re.IGNORECASE)


def _domain(address: str) -> str:
    parsed = getaddresses([address])
    if not parsed or "@" not in parsed[0][1]:
        return ""
    return parsed[0][1].rsplit("@", 1)[1].lower().rstrip(">")


def _contains_any(text: str, terms: set[str]) -> int:
    words = set(re.findall(r"[a-z0-9-]+", text.lower()))
    return int(bool(words & terms))


def _url_host(url: str) -> str:
    try:
        return urlparse(url if "://" in url else f"http://{url}").hostname or ""
    except ValueError:
        return ""


def _link_text_mismatch(url: str, label: str) -> bool:
    displayed_url = _URL.search(label)
    if not displayed_url:
        return False
    destination = _url_host(url)
    displayed_host = _url_host(displayed_url.group(0))
    return bool(destination and displayed_host and destination.lower() != displayed_host.lower())


def extract_features(email: ParsedEmail) -> dict[str, float]:
    cleaned = prepare_email(email)
    subject = cleaned["subject"]
    body = cleaned["body"]
    combined = f"{subject} {body}"
    urls = _URL.findall(body) + [url for url, _ in email.links]
    normalized_urls = [url.rstrip(".,;:!?)]}") for url in urls]
    hosts = [_url_host(url) for url in normalized_urls]
    unique_urls = set(normalized_urls)
    sender_domain = _domain(email.sender)
    reply_domain = _domain(email.reply_to)
    return_path_domain = _domain(email.return_path)
    display_name, sender_address = getaddresses([email.sender])[0] if email.sender else ("", "")
    sender_name_mismatch = int(
        bool(display_name and sender_address and sender_domain not in display_name.lower())
        and any(term in display_name.lower() for term in {"support", "security", "billing", "admin"})
    )
    authenticators = " ".join(email.headers.get("authentication-results", "").lower().split())
    uppercase_letters = sum(character.isupper() for character in combined)
    letters = sum(character.isalpha() for character in combined)
    external_hosts = {host.lower() for host in hosts if host}
    sender_hosts = {sender_domain} if sender_domain else set()
    count_words = Counter(re.findall(r"[a-z0-9-]+", combined.lower()))

    values = {
        "subject_length": len(subject),
        "body_length": len(body),
        "word_count": len(re.findall(r"\b\w+\b", combined)),
        "url_count": len(normalized_urls),
        "unique_url_count": len(unique_urls),
        "ip_url_count": sum(bool(_IP_HOST.fullmatch(host)) for host in hosts),
        "shortener_url_count": sum(host.lower() in _SHORTENERS for host in hosts),
        "https_url_ratio": (
            sum(url.lower().startswith("https://") for url in normalized_urls) / len(normalized_urls)
            if normalized_urls else 0.0
        ),
        "email_address_count": len(_EMAIL.findall(combined)),
        "sender_reply_to_domain_mismatch": int(bool(sender_domain and reply_domain and sender_domain != reply_domain)),
        "sender_return_path_domain_mismatch": int(bool(sender_domain and return_path_domain and sender_domain != return_path_domain)),
        "sender_display_name_mismatch": sender_name_mismatch,
        "urgency_word_count": sum(count_words[word] for word in _URGENCY),
        "credential_word_count": sum(count_words[word] for word in _CREDENTIALS),
        "financial_word_count": sum(count_words[word] for word in _FINANCIAL),
        "threat_word_count": sum(count_words[word] for word in _THREATS),
        "exclamation_count": combined.count("!"),
        "uppercase_ratio": uppercase_letters / letters if letters else 0.0,
        "subject_has_reply_prefix": int(bool(re.match(r"^\s*(re|fwd?|fw)\s*:", subject, re.IGNORECASE))),
        "subject_has_urgent_term": _contains_any(subject, _URGENCY),
        "subject_has_financial_term": _contains_any(subject, _FINANCIAL),
        "subject_is_empty": int(not bool(subject)),
        "body_has_greeting": int(bool(_GREETING.search(body))),
        "body_has_signature": int(bool(_SIGNATURE.search(body))),
        "html_has_form": int(bool(re.search(r"<form\b", email.html_body, re.IGNORECASE))),
        "html_has_password_input": int(bool(re.search(r"<input\b[^>]*type\s*=\s*['\"]?password", email.html_body, re.IGNORECASE))),
        "html_has_iframe": int(bool(re.search(r"<iframe\b", email.html_body, re.IGNORECASE))),
        "html_has_hidden_element": int(bool(re.search(r"display\s*:\s*none|visibility\s*:\s*hidden|hidden\b", email.html_body, re.IGNORECASE))),
        "html_has_script": int(bool(re.search(r"<script\b", email.html_body, re.IGNORECASE))),
        "has_attachment": int(bool(email.attachments)),
        "attachment_count": len(email.attachments),
        "has_received_header": int("received" in email.headers),
        "spf_pass": int(bool(re.search(r"\bspf\s*=\s*pass\b", authenticators))),
        "dkim_pass": int(bool(re.search(r"\bdkim\s*=\s*pass\b", authenticators))),
        "dmarc_pass": int(bool(re.search(r"\bdmarc\s*=\s*pass\b", authenticators))),
        "body_has_control_character": int(
            any(unicodedata.category(char) in {"Cc", "Cf"} for char in body if char not in "\t\n\r")
        ),
        "link_text_mismatch_count": sum(
            _link_text_mismatch(url, label) for url, label in email.links
        ),
        "url_uses_punycode": int(any("xn--" in host.lower() for host in hosts)),
        "sender_uses_free_email": int(sender_domain in _FREE_EMAIL),
        "external_url_count": len(external_hosts - sender_hosts),
    }
    return {name: float(values[name]) for name in FEATURE_NAMES}
