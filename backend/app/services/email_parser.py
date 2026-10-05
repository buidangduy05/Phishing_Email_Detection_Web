from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
from html.parser import HTMLParser
from typing import Any


class _VisibleHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.links: list[tuple[str, str]] = []
        self._hidden_depth = 0
        self._current_link: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag in {"script", "style", "head"}:
            self._hidden_depth += 1
        if tag == "a" and attributes.get("href"):
            self._current_link = {"href": attributes["href"] or "", "text": ""}
        if tag == "br" or tag in {"p", "div", "li", "tr"}:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "head"} and self._hidden_depth:
            self._hidden_depth -= 1
        if tag == "a" and self._current_link is not None:
            self.links.append((self._current_link["href"], self._current_link["text"]))
            self._current_link = None
        if tag in {"p", "div", "li", "tr"}:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        if self._hidden_depth:
            return
        self.parts.append(data)
        if self._current_link is not None:
            self._current_link["text"] += data


@dataclass(frozen=True)
class ParsedEmail:
    subject: str
    sender: str
    recipients: tuple[str, ...]
    reply_to: str
    return_path: str
    body: str
    html_body: str
    links: tuple[tuple[str, str], ...]
    headers: dict[str, str]
    attachments: tuple[str, ...]


def parse_email(raw_email: bytes) -> ParsedEmail:
    message = BytesParser(policy=policy.default).parsebytes(raw_email)
    if not message.items():
        raise ValueError("The uploaded file does not contain valid email headers.")

    plain_parts: list[str] = []
    html_parts: list[str] = []
    attachments: list[str] = []
    for part in message.walk():
        if part.is_multipart():
            continue
        filename = part.get_filename()
        if filename or part.get_content_disposition() == "attachment":
            attachments.append(filename or "unnamed attachment")
            continue
        content_type = part.get_content_type()
        if content_type not in {"text/plain", "text/html"}:
            continue
        try:
            content: Any = part.get_content()
        except (LookupError, UnicodeError, ValueError):
            payload = part.get_payload(decode=True) or b""
            content = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        if not isinstance(content, str):
            continue
        if content_type == "text/plain":
            plain_parts.append(content)
        else:
            html_parts.append(content)

    html_body = "\n".join(html_parts)
    html_parser = _VisibleHTML()
    if html_body:
        html_parser.feed(html_body)
        html_parser.close()

    headers = {name.lower(): str(value) for name, value in message.items()}
    return ParsedEmail(
        subject=str(message.get("subject", "")),
        sender=str(message.get("from", "")),
        recipients=tuple(
            str(message.get(name, ""))
            for name in ("to", "cc", "bcc")
            if message.get(name)
        ),
        reply_to=str(message.get("reply-to", "")),
        return_path=str(message.get("return-path", "")),
        body="\n".join(plain_parts) or " ".join(html_parser.parts),
        html_body=html_body,
        links=tuple(html_parser.links),
        headers=headers,
        attachments=tuple(attachments),
    )
