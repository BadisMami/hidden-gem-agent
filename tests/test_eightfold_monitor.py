import sys
import os

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "src", "company_monitors")
)

import eightfold_monitor  # noqa: E402


class FakeResponse:

    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


# count=12 (> page_size=10) forces a second page fetch at start=10.
PAGE_1 = {
    "data": {
        "count": 12,
        "positions": [
            {
                "id": 1001,
                "name": "Software Engineer Intern",
                "locations": ["Moline,Illinois,United States"],
                "positionUrl": "/careers/job/1001",
            },
            {
                # Substring false-positive that must be filtered out.
                "id": 1002,
                "name": "Internal Auditor",
                "locations": ["Moline,Illinois,United States"],
                "positionUrl": "/careers/job/1002",
            },
        ]
    }
}

PAGE_2 = {
    "data": {
        "count": 12,
        "positions": [
            {
                "id": 1003,
                "name": "Data Science Intern",
                "locations": ["Remote"],
                "positionUrl": "/careers/job/1003",
            },
        ]
    }
}

EMPTY_PAGE = {"data": {"count": 12, "positions": []}}


def test_filters_internal_false_positive_and_paginates(monkeypatch):

    calls = {"count": 0}

    def fake_get(url, params, headers, timeout):
        calls["count"] += 1
        start = params["start"]
        if start == 0:
            return FakeResponse(PAGE_1)
        elif start == 10:
            return FakeResponse(PAGE_2)
        return FakeResponse(EMPTY_PAGE)

    monkeypatch.setattr(eightfold_monitor.requests, "get", fake_get)

    results = eightfold_monitor.get_eightfold_internships(
        "Acme", "careers.acme.com", "acme.com"
    )

    titles = {r["title"] for r in results}

    assert "Internal Auditor" not in titles
    assert "Software Engineer Intern" in titles
    assert "Data Science Intern" in titles
    assert len(results) == 2


def test_absolute_and_relative_urls_handled(monkeypatch):

    def fake_get(url, params, headers, timeout):
        return FakeResponse(PAGE_1)

    monkeypatch.setattr(eightfold_monitor.requests, "get", fake_get)

    results = eightfold_monitor.get_eightfold_internships(
        "Acme", "careers.acme.com", "acme.com"
    )

    by_id = {r["external_job_id"]: r for r in results}

    assert by_id["1001"]["application_url"] == \
        "https://careers.acme.com/careers/job/1001"
    assert by_id["1001"]["source_platform"] == "eightfold"


def test_network_failure_returns_empty_list(monkeypatch):

    def raise_error(url, params, headers, timeout):
        raise ConnectionError("boom")

    monkeypatch.setattr(eightfold_monitor.requests, "get", raise_error)

    results = eightfold_monitor.get_eightfold_internships(
        "Acme", "careers.acme.com", "acme.com"
    )

    assert results == []
