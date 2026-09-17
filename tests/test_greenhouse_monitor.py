import sys
import os

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "src", "company_monitors")
)

import greenhouse_monitor  # noqa: E402


class FakeResponse:

    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


FIXTURE_JOBS = {
    "jobs": [
        {
            "id": 1001,
            "title": "Software Engineering Intern",
            "location": {"name": "Lincoln, NE"},
            "absolute_url": "https://job-boards.greenhouse.io/acme/jobs/1001",
            "metadata": [
                {"name": "Employment Type", "value": "Intern (Trainee)"}
            ],
        },
        {
            # Title doesn't say "intern" - only metadata does.
            "id": 1002,
            "title": "Product Management",
            "location": {"name": "Lincoln, NE"},
            "absolute_url": "https://job-boards.greenhouse.io/acme/jobs/1002",
            "metadata": [
                {"name": "Employment Type", "value": "Intern"}
            ],
        },
        {
            # Full-time role - must be excluded.
            "id": 1003,
            "title": "Senior Software Engineer",
            "location": {"name": "Lincoln, NE"},
            "absolute_url": "https://job-boards.greenhouse.io/acme/jobs/1003",
            "metadata": [
                {"name": "Employment Type", "value": "Full-Time"}
            ],
        },
        {
            # Anchor-tag-polluted URL should be cleaned.
            "id": 1004,
            "title": "Machine Learning Intern",
            "location": {"name": "Remote"},
            "absolute_url": (
                '<a href="https://job-boards.greenhouse.io/acme/jobs/1004">'
                "Apply</a>"
            ),
            "metadata": [],
        },
    ]
}


def test_filters_by_title_and_metadata(monkeypatch):

    monkeypatch.setattr(
        greenhouse_monitor.requests,
        "get",
        lambda url, timeout: FakeResponse(FIXTURE_JOBS)
    )

    results = greenhouse_monitor.get_greenhouse_internships("Acme", "acme")

    titles = {r["title"] for r in results}

    assert "Software Engineering Intern" in titles
    assert "Product Management" in titles  # caught via metadata
    assert "Senior Software Engineer" not in titles  # not an internship
    assert "Machine Learning Intern" in titles

    assert len(results) == 3


def test_role_classification_and_ids(monkeypatch):

    monkeypatch.setattr(
        greenhouse_monitor.requests,
        "get",
        lambda url, timeout: FakeResponse(FIXTURE_JOBS)
    )

    results = greenhouse_monitor.get_greenhouse_internships("Acme", "acme")

    by_id = {r["external_job_id"]: r for r in results}

    assert by_id["1001"]["role_type"] == "SWE"
    assert by_id["1002"]["role_type"] == "Product"
    assert by_id["1004"]["role_type"] == "ML"

    for r in results:
        assert r["source_platform"] == "greenhouse"
        assert r["company"] == "Acme"


def test_url_is_cleaned_of_html(monkeypatch):

    monkeypatch.setattr(
        greenhouse_monitor.requests,
        "get",
        lambda url, timeout: FakeResponse(FIXTURE_JOBS)
    )

    results = greenhouse_monitor.get_greenhouse_internships("Acme", "acme")

    by_id = {r["external_job_id"]: r for r in results}

    assert by_id["1004"]["application_url"] == \
        "https://job-boards.greenhouse.io/acme/jobs/1004"

    assert "<a href" not in by_id["1004"]["application_url"]


def test_network_failure_returns_empty_list(monkeypatch):

    def raise_error(url, timeout):
        raise ConnectionError("boom")

    monkeypatch.setattr(greenhouse_monitor.requests, "get", raise_error)

    results = greenhouse_monitor.get_greenhouse_internships("Acme", "acme")

    assert results == []
