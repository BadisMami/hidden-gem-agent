import sys
import os

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "src", "company_monitors")
)

import workday_monitor  # noqa: E402


class FakeResponse:

    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def _posting(title, path, req_id, location="Reston, VA"):
    return {
        "title": title,
        "externalPath": path,
        "locationsText": location,
        "bulletFields": [req_id],
    }


FULL_PAGE_OF_INTERNS = {
    "jobPostings": [
        _posting(f"Software Engineering Intern {i}", f"/job/x/SWE_{i}", f"R{i}")
        for i in range(20)
    ]
}

# Page 2: relevance has run out - fuzzy matches only.
PAGE_OF_NON_INTERNS = {
    "jobPostings": [
        _posting("International Trade Analyst", "/job/x/ITA", "R900"),
    ] * 20
}


def test_parses_postings_and_builds_apply_url(monkeypatch):

    payload = {"jobPostings": [
        _posting("FPGA Design Intern", "/job/Reston-VA/FPGA_R123", "R123"),
        _posting("International Trade Analyst", "/job/x/ITA", "R900"),
    ]}

    monkeypatch.setattr(
        workday_monitor.requests, "post",
        lambda url, json, headers, timeout: FakeResponse(payload)
    )

    results = workday_monitor.get_workday_internships(
        "Leidos", "leidos.wd5.myworkdayjobs.com", "leidos", "External"
    )

    assert len(results) == 1
    job = results[0]
    assert job["title"] == "FPGA Design Intern"
    assert job["role_type"] == "Hardware"
    assert job["external_job_id"] == "R123"
    assert job["source_platform"] == "workday"
    assert job["application_url"] == (
        "https://leidos.wd5.myworkdayjobs.com/en-US/External"
        "/job/Reston-VA/FPGA_R123"
    )


def test_pages_until_a_page_has_no_internships(monkeypatch):

    calls = []

    def fake_post(url, json, headers, timeout):
        calls.append(json["offset"])
        return FakeResponse(
            FULL_PAGE_OF_INTERNS if json["offset"] == 0
            else PAGE_OF_NON_INTERNS
        )

    monkeypatch.setattr(workday_monitor.requests, "post", fake_post)

    results = workday_monitor.get_workday_internships(
        "Leidos", "leidos.wd5.myworkdayjobs.com", "leidos", "External"
    )

    assert len(results) == 20
    assert calls == [0, 20]


def test_network_failure_returns_empty_list(monkeypatch):

    def raise_error(url, json, headers, timeout):
        raise ConnectionError("boom")

    monkeypatch.setattr(workday_monitor.requests, "post", raise_error)

    assert workday_monitor.get_workday_internships(
        "Leidos", "leidos.wd5.myworkdayjobs.com", "leidos", "External"
    ) == []
