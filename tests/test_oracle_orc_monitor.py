import sys
import os

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "src", "company_monitors")
)

import oracle_orc_monitor  # noqa: E402


class FakeResponse:

    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def make_page(total_count, requisitions):
    return {
        "items": [
            {
                "TotalJobsCount": total_count,
                "requisitionList": requisitions,
            }
        ]
    }


PAGE_1 = make_page(
    30,
    [
        {
            "Id": 155591,
            "Title": "Marketing - Summer 2027 Intern",
            "PrimaryLocation": "United States",
        },
        {
            # Substring false-positive that must be filtered out.
            "Id": 156497,
            "Title": "Internal Audit Manager",
            "PrimaryLocation": "Charlotte, NC, United States",
        },
    ]
)

PAGE_2 = make_page(
    30,
    [
        {
            "Id": 155522,
            "Title": "Artificial Intelligence/Machine Learning - "
                      "Summer 2027 Intern",
            "PrimaryLocation": "United States",
        },
    ]
)

EMPTY_PAGE = make_page(30, [])


def test_filters_internal_false_positive_and_paginates(monkeypatch):

    def fake_get(url, params, headers, timeout):
        offset = int(params["finder"].split("offset=")[1])
        if offset == 0:
            return FakeResponse(PAGE_1)
        elif offset == 25:
            return FakeResponse(PAGE_2)
        return FakeResponse(EMPTY_PAGE)

    monkeypatch.setattr(oracle_orc_monitor.requests, "get", fake_get)

    results = oracle_orc_monitor.get_oracle_orc_internships(
        "Acme", "careers.acme.com", "acme.fa.ocs.oraclecloud.com",
        "CX_1", "Acme"
    )

    titles = {r["title"] for r in results}

    assert "Internal Audit Manager" not in titles
    assert "Marketing - Summer 2027 Intern" in titles
    assert "Artificial Intelligence/Machine Learning - Summer 2027 Intern" \
        in titles
    assert len(results) == 2


def test_application_url_uses_site_name_not_site_number(monkeypatch):

    def fake_get(url, params, headers, timeout):
        return FakeResponse(make_page(1, PAGE_1["items"][0]["requisitionList"]))

    monkeypatch.setattr(oracle_orc_monitor.requests, "get", fake_get)

    results = oracle_orc_monitor.get_oracle_orc_internships(
        "Acme", "careers.acme.com", "acme.fa.ocs.oraclecloud.com",
        "CX_1", "AcmeCorp"
    )

    by_id = {r["external_job_id"]: r for r in results}

    assert by_id["155591"]["application_url"] == \
        "https://careers.acme.com/en/sites/AcmeCorp/job/155591"
    assert "CX_1" not in by_id["155591"]["application_url"]
    assert by_id["155591"]["source_platform"] == "oracle_orc"


def test_network_failure_returns_empty_list(monkeypatch):

    def raise_error(url, params, headers, timeout):
        raise ConnectionError("boom")

    monkeypatch.setattr(oracle_orc_monitor.requests, "get", raise_error)

    results = oracle_orc_monitor.get_oracle_orc_internships(
        "Acme", "careers.acme.com", "acme.fa.ocs.oraclecloud.com",
        "CX_1", "Acme"
    )

    assert results == []
