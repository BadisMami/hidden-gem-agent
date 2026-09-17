import sys
import os

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "src", "company_monitors")
)

import jibe_monitor  # noqa: E402


class FakeResponse:

    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


FIXTURE = {
    "jobs": [
        {
            "data": {
                "req_id": "20080",
                "slug": "20080",
                "title": "Software Engineer Intern - Aviation",
                "full_location": "Middlebury, Connecticut",
                "tags3": ["Intern"],
                "apply_url": "https://careers-acme.icims.com/jobs/20080/login",
            }
        },
        {
            "data": {
                "req_id": "20081",
                "slug": "20081",
                "title": "Data Scientist Intern",
                "full_location": "Olathe, Kansas",
                "tags3": ["Intern"],
                "apply_url": "https://careers-acme.icims.com/jobs/20081/login",
            }
        },
        {
            # Not actually an internship - must be filtered out even
            # though it slipped past a server-side filter.
            "data": {
                "req_id": "1",
                "slug": "1",
                "title": "Senior Engineer",
                "full_location": "Olathe, Kansas",
                "tags3": ["Regular Full-Time"],
                "apply_url": "https://careers-acme.icims.com/jobs/1/login",
            }
        },
        {
            # No apply_url - should fall back to canonical_url.
            "data": {
                "req_id": "20082",
                "slug": "20082",
                "title": "Mechanical Engineering Intern",
                "full_location": "Cary, North Carolina",
                "tags3": ["Intern"],
                "canonical_url": "https://careers.acme.com/jobs/20082",
            }
        },
    ]
}


def test_filters_to_intern_tag_only(monkeypatch):

    monkeypatch.setattr(
        jibe_monitor.requests,
        "get",
        lambda url, params, headers, timeout: FakeResponse(FIXTURE)
    )

    results = jibe_monitor.get_jibe_internships("Acme", "careers.acme.com")

    titles = {r["title"] for r in results}

    assert "Software Engineer Intern - Aviation" in titles
    assert "Data Scientist Intern" in titles
    assert "Mechanical Engineering Intern" in titles
    assert "Senior Engineer" not in titles
    assert len(results) == 3


def test_role_classification_and_schema(monkeypatch):

    monkeypatch.setattr(
        jibe_monitor.requests,
        "get",
        lambda url, params, headers, timeout: FakeResponse(FIXTURE)
    )

    results = jibe_monitor.get_jibe_internships("Acme", "careers.acme.com")

    by_id = {r["external_job_id"]: r for r in results}

    assert by_id["20080"]["role_type"] == "SWE"
    assert by_id["20081"]["role_type"] == "Data"

    for r in results:
        assert r["source_platform"] == "jibe"
        assert r["company"] == "Acme"


def test_falls_back_to_canonical_url_when_no_apply_url(monkeypatch):

    monkeypatch.setattr(
        jibe_monitor.requests,
        "get",
        lambda url, params, headers, timeout: FakeResponse(FIXTURE)
    )

    results = jibe_monitor.get_jibe_internships("Acme", "careers.acme.com")

    by_id = {r["external_job_id"]: r for r in results}

    assert by_id["20082"]["application_url"] == \
        "https://careers.acme.com/jobs/20082"


def test_network_failure_returns_empty_list(monkeypatch):

    def raise_error(url, params, headers, timeout):
        raise ConnectionError("boom")

    monkeypatch.setattr(jibe_monitor.requests, "get", raise_error)

    results = jibe_monitor.get_jibe_internships("Acme", "careers.acme.com")

    assert results == []


def test_no_internships_returns_empty_list(monkeypatch):

    monkeypatch.setattr(
        jibe_monitor.requests,
        "get",
        lambda url, params, headers, timeout: FakeResponse({"jobs": []})
    )

    results = jibe_monitor.get_jibe_internships("Acme", "careers.acme.com")

    assert results == []
