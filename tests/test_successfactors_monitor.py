import sys
import os

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "src", "company_monitors")
)

import successfactors_monitor  # noqa: E402


class FakeResponse:

    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass


def _row(title, href, location):
    # Real pages render the title link twice per row (desktop + mobile).
    link = f'<a href="{href}" class="jobTitle-link">{title}</a>'
    return (
        f'<tr class="data-row">{link}{link}'
        f'<span class="jobLocation">\n  {location}\n</span></tr>'
    )


PAGE = "<table>" + "".join([
    _row("EMBEDDED SOFTWARE ENGINEER INTERN",
         "/job/Newport-News-Embedded-Intern/1234567/", "Newport News, VA"),
    _row("INTERNAL AUDITOR 3",
         "/job/Newport-News-Internal-Auditor/7654321/", "Newport News, VA"),
    _row("Systems &amp; Software Co-op",
         "/job/Pascagoula-Co-op/1111111/", "Pascagoula, MS"),
]) + "</table>"


def test_parses_rows_dedups_and_filters(monkeypatch):

    monkeypatch.setattr(
        successfactors_monitor.requests, "get",
        lambda url, params, headers, timeout: FakeResponse(PAGE)
    )

    results = successfactors_monitor.get_successfactors_internships(
        "HII", "careers.huntingtoningalls.com"
    )

    assert [r["title"] for r in results] == [
        "EMBEDDED SOFTWARE ENGINEER INTERN",
        "Systems & Software Co-op",
    ]

    first = results[0]
    assert first["role_type"] == "Embedded"
    assert first["location"] == "Newport News, VA"
    assert first["external_job_id"] == "1234567"
    assert first["application_url"] == (
        "https://careers.huntingtoningalls.com"
        "/job/Newport-News-Embedded-Intern/1234567/"
    )


def test_network_failure_returns_empty_list(monkeypatch):

    def raise_error(url, params, headers, timeout):
        raise ConnectionError("boom")

    monkeypatch.setattr(successfactors_monitor.requests, "get", raise_error)

    assert successfactors_monitor.get_successfactors_internships(
        "HII", "careers.huntingtoningalls.com"
    ) == []
