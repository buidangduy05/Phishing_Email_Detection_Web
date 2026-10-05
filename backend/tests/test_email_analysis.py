import unittest

from app.services.email_parser import parse_email
from app.services.feature_extractor import FEATURE_NAMES, extract_features
from app.services.preprocessing import prepare_email, tokenize


SAMPLE_EMAIL = b"""From: PayPal Security <alerts@paypal-notify.example>
Reply-To: account@other.example
Return-Path: <bounce@paypal-notify.example>
To: recipient@example.net
Subject: Urgent: verify your account now!
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="mailguard-boundary"

--mailguard-boundary
Content-Type: text/plain; charset="utf-8"

Dear customer, verify your password immediately at https://bit.ly/account
--mailguard-boundary
Content-Type: text/html; charset="utf-8"

<html><body><form><input type="password"><a href="https://evil.example/login">https://paypal.com</a></form><div style="display:none">hidden</div><iframe></iframe></body></html>
--mailguard-boundary--
"""


class EmailAnalysisTests(unittest.TestCase):
    def test_extracts_exactly_forty_stable_features(self) -> None:
        parsed_email = parse_email(SAMPLE_EMAIL)
        features = extract_features(parsed_email)

        self.assertEqual(tuple(features), FEATURE_NAMES)
        self.assertEqual(len(features), 40)
        self.assertEqual(features["sender_reply_to_domain_mismatch"], 1)
        self.assertEqual(features["shortener_url_count"], 1)
        self.assertEqual(features["html_has_password_input"], 1)
        self.assertEqual(features["link_text_mismatch_count"], 1)
        self.assertEqual(features["html_has_hidden_element"], 1)

    def test_preprocessing_returns_clean_text_and_tokens(self) -> None:
        email = parse_email(SAMPLE_EMAIL)
        cleaned = prepare_email(email)

        self.assertIn("Urgent: verify your account now!", cleaned["subject"])
        self.assertIn("password", tokenize(cleaned["body"]))

    def test_rejects_content_without_email_headers(self) -> None:
        with self.assertRaises(ValueError):
            parse_email(b"not an email message")

    def test_malformed_url_does_not_break_feature_extraction(self) -> None:
        message = b"""From: sender@example.com
To: receiver@example.com
Subject: link
Content-Type: text/html

<a href="https://[invalid">https://example.com</a>
"""
        features = extract_features(parse_email(message))

        self.assertEqual(len(features), 40)


if __name__ == "__main__":
    unittest.main()
