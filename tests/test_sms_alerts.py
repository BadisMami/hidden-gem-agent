import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import sms_alerts  # noqa: E402


def _clear_env(monkeypatch):
    for var in (
        "EMAIL_SENDER_ADDRESS",
        "EMAIL_APP_PASSWORD",
        "NOTIFICATION_PHONE_NUMBER",
        "SMS_CARRIER_GATEWAY",
    ):
        monkeypatch.delenv(var, raising=False)


def test_missing_config_skips_without_error(monkeypatch):

    _clear_env(monkeypatch)

    result = sms_alerts.send_sms_alert("test message")

    assert result is False


def test_partial_config_skips(monkeypatch):

    _clear_env(monkeypatch)
    monkeypatch.setenv("EMAIL_SENDER_ADDRESS", "me@gmail.com")
    monkeypatch.setenv("NOTIFICATION_PHONE_NUMBER", "4075551234")
    # EMAIL_APP_PASSWORD and SMS_CARRIER_GATEWAY intentionally left unset.

    result = sms_alerts.send_sms_alert("test message")

    assert result is False


def test_sends_via_smtp_when_fully_configured(monkeypatch):

    _clear_env(monkeypatch)
    monkeypatch.setenv("EMAIL_SENDER_ADDRESS", "me@gmail.com")
    monkeypatch.setenv("EMAIL_APP_PASSWORD", "app-password")
    monkeypatch.setenv("NOTIFICATION_PHONE_NUMBER", "4075551234")
    monkeypatch.setenv("SMS_CARRIER_GATEWAY", "tmomail.net")

    sent = {}

    class FakeSMTP:

        def __init__(self, host, port, timeout=None):
            sent["host"] = host
            sent["port"] = port

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def starttls(self):
            sent["starttls"] = True

        def login(self, user, password):
            sent["login"] = (user, password)

        def send_message(self, message):
            sent["message"] = message

    monkeypatch.setattr(sms_alerts.smtplib, "SMTP", FakeSMTP)

    result = sms_alerts.send_sms_alert("New internship!")

    assert result is True
    assert sent["host"] == "smtp.gmail.com"
    assert sent["login"] == ("me@gmail.com", "app-password")
    assert sent["message"]["To"] == "4075551234@tmomail.net"
    assert sent["message"]["From"] == "me@gmail.com"
    assert sent["message"].get_content().strip() == "New internship!"


def test_smtp_failure_returns_false_not_raise(monkeypatch):

    _clear_env(monkeypatch)
    monkeypatch.setenv("EMAIL_SENDER_ADDRESS", "me@gmail.com")
    monkeypatch.setenv("EMAIL_APP_PASSWORD", "app-password")
    monkeypatch.setenv("NOTIFICATION_PHONE_NUMBER", "4075551234")
    monkeypatch.setenv("SMS_CARRIER_GATEWAY", "tmomail.net")

    class ExplodingSMTP:

        def __init__(self, host, port, timeout=None):
            pass

        def __enter__(self):
            raise ConnectionRefusedError("boom")

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(sms_alerts.smtplib, "SMTP", ExplodingSMTP)

    result = sms_alerts.send_sms_alert("New internship!")

    assert result is False
