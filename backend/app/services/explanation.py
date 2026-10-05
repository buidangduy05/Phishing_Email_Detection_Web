from app.services.feature_extractor import FEATURE_NAMES


_INDICATORS = {
    "sender_reply_to_domain_mismatch": ("Reply-to address differs", "The reply-to address uses a different domain from the sender."),
    "sender_return_path_domain_mismatch": ("Sender routing mismatch", "The return-path domain differs from the sender domain."),
    "sender_display_name_mismatch": ("Unusual sender display name", "The sender name claims a trusted role but does not match the sender address."),
    "urgency_word_count": ("Urgent language", "The message pressures the recipient to act quickly."),
    "credential_word_count": ("Credential request language", "The message mentions account sign-in, password, or verification."),
    "financial_word_count": ("Financial language", "The message discusses payments, banking, or financial details."),
    "threat_word_count": ("Threatening account language", "The message warns of suspension, closure, or other consequences."),
    "shortener_url_count": ("Shortened link", "A link uses a URL-shortening service, which hides its destination."),
    "ip_url_count": ("Link points to an IP address", "At least one URL uses a raw IP address instead of a domain name."),
    "html_has_form": ("Embedded form", "The HTML email contains a form that could collect information."),
    "html_has_password_input": ("Password field in email", "The HTML email contains a password input field."),
    "html_has_iframe": ("Embedded iframe", "The HTML email contains an embedded frame."),
    "html_has_hidden_element": ("Hidden HTML content", "The HTML email contains content hidden from the reader."),
    "url_uses_punycode": ("Internationalized URL domain", "A URL uses punycode, which can make look-alike domains harder to spot."),
    "link_text_mismatch_count": ("Link text and destination differ", "A displayed link points to a different domain than its destination."),
    "exclamation_count": ("Excessive exclamation marks", "The message uses emphatic punctuation."),
}


def explain_risks(features: dict[str, float]) -> list[dict[str, str]]:
    explanations = []
    for name in FEATURE_NAMES:
        if features.get(name, 0) <= 0 or name not in _INDICATORS:
            continue
        title, description = _INDICATORS[name]
        explanations.append({"title": title, "description": description})
    return explanations
