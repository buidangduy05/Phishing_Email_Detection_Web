import re
import unicodedata

from app.services.email_parser import ParsedEmail


_WHITESPACE = re.compile(r"\s+")
_HTML_TAG = re.compile(r"<[^>]+>")


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = _HTML_TAG.sub(" ", text)
    return _WHITESPACE.sub(" ", text).strip()


def prepare_email(email: ParsedEmail) -> dict[str, str]:
    return {
        "subject": clean_text(email.subject),
        "body": clean_text(email.body),
        "sender": clean_text(email.sender),
        "reply_to": clean_text(email.reply_to),
        "return_path": clean_text(email.return_path),
    }


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())
