import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import internship_monitor_service as svc  # noqa: E402


def _make_internship(company, title, location="Remote", url="https://example.com/job/1"):
    return {
        "company": company,
        "title": title,
        "location": location,
        "application_url": url,
    }


def test_single_alert_uses_full_detail_format():

    alerts = [_make_internship("Acme", "SWE Intern", "Remote", "https://acme.com/j/1")]

    body = svc._build_batch_sms_body(alerts)

    assert "Acme" in body
    assert "SWE Intern" in body
    assert "https://acme.com/j/1" in body


def test_multiple_alerts_produce_one_consolidated_message():

    alerts = [
        _make_internship("Acme", "SWE Intern"),
        _make_internship("Globex", "ML Intern"),
        _make_internship("Initech", "Data Intern"),
    ]

    body = svc._build_batch_sms_body(alerts)

    # One message, not one per internship - all companies appear in it.
    assert "3 new internships" in body
    assert "Acme" in body
    assert "Globex" in body
    assert "Initech" in body


def test_large_batch_is_one_message_listing_everything():
    """
    Regression test: the bug that got 40 SEPARATE texts sent in one run
    and bounced from the carrier gateway. A large batch must still be
    exactly one send (one call to send_sms_alert / one SMTP transaction)
    - that's what avoids the carrier's burst-spam detection, regardless
    of how many postings end up listed inside that single message.
    """

    alerts = [
        _make_internship(f"Company{i}", f"Intern Role {i}")
        for i in range(40)
    ]

    body = svc._build_batch_sms_body(alerts)

    assert "40 new internships" in body

    # Every posting gets its own line, all within the one message body.
    listed_lines = [
        line for line in body.split("\n") if line.startswith("- Company")
    ]
    assert len(listed_lines) == 40
    assert "Company0" in body
    assert "Company39" in body
