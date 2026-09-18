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


def test_same_role_same_company_grouped_with_all_links():
    """
    User request: when a company opens several reqs under the same
    title (e.g. 5 "Software Engineering Intern" postings at once), show
    one "Title - Company" header followed by all 5 links back to back,
    rather than repeating the title/company on every line.
    """

    alerts = [
        _make_internship(
            "Lockheed Martin", "Embedded Software Engineer Intern",
            "Fort Worth, TX", "https://lm.com/job/1"
        ),
        _make_internship(
            "Lockheed Martin", "Embedded Software Engineer Intern",
            "Austin, TX", "https://lm.com/job/2"
        ),
        _make_internship(
            "Lockheed Martin", "Embedded Software Engineer Intern",
            "Remote", "https://lm.com/job/3"
        ),
        _make_internship(
            "Lockheed Martin", "Embedded Software Engineer Intern",
            "Denver, CO", "https://lm.com/job/4"
        ),
        _make_internship(
            "Lockheed Martin", "Embedded Software Engineer Intern",
            "Orlando, FL", "https://lm.com/job/5"
        ),
        _make_internship(
            "Boeing", "Software Engineering Intern",
            "Seattle, WA", "https://boeing.com/job/9"
        ),
    ]

    body = svc._build_batch_sms_body(alerts)

    assert "6 new internships found" in body
    # One header for the 5 identically-titled Lockheed Martin postings.
    assert body.count("Embedded Software Engineer Intern - Lockheed Martin") == 1
    assert body.count("Software Engineering Intern - Boeing") == 1

    for i in range(1, 6):
        assert f"https://lm.com/job/{i}" in body

    assert "https://boeing.com/job/9" in body


def test_large_batch_is_one_message_listing_everything():
    """
    Regression test: the bug that got 40 SEPARATE texts sent in one run
    and bounced from the carrier gateway. A large batch must still be
    exactly one send (one call to send_sms_alert / one SMTP transaction)
    - that's what avoids the carrier's burst-spam detection, regardless
    of how many postings end up listed inside that single message.
    """

    alerts = [
        _make_internship(
            f"Company{i}", f"Intern Role {i}", url=f"https://example.com/job/{i}"
        )
        for i in range(40)
    ]

    body = svc._build_batch_sms_body(alerts)

    assert "40 new internships" in body

    # Each of the 40 distinct roles gets its own header line.
    header_lines = [
        line for line in body.split("\n")
        if line.startswith("Intern Role")
    ]
    assert len(header_lines) == 40
    assert "Company0" in body
    assert "Company39" in body
    assert "https://example.com/job/0" in body
    assert "https://example.com/job/39" in body
