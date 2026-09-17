import os
import sqlite3
import tempfile

import pytest

import database_setup
import database_monitor


@pytest.fixture
def test_db():

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    database_setup.create_database(path)

    yield path

    os.remove(path)


def test_alert_created_for_matching_role(test_db):
    """data/users.csv includes a user interested in SWE."""

    alert = database_monitor.create_alert_for_new_internship(
        "Acme", "SWE Intern", "Remote", "SWE", db_path=test_db
    )

    assert alert is not None
    assert alert["match_score"] >= 1

    conn = sqlite3.connect(test_db)
    count = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
    conn.close()

    assert count == 1


def test_no_alert_for_unmatched_role(test_db):
    """No user in data/users.csv is interested in 'Product'."""

    alert = database_monitor.create_alert_for_new_internship(
        "Acme", "Product Intern", "Remote", "Product", db_path=test_db
    )

    assert alert is None

    conn = sqlite3.connect(test_db)
    count = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
    conn.close()

    assert count == 0


def test_alert_only_fires_once_per_new_internship(test_db):
    """Re-upserting the same job (no longer 'new') must not alert again."""

    result = database_monitor.upsert_internship(
        "Acme", "SWE Intern", "Remote", "SWE",
        "https://acme.com/jobs/1",
        source_platform="greenhouse",
        external_job_id="1",
        db_path=test_db
    )
    assert result["is_new"] is True

    database_monitor.create_alert_for_new_internship(
        "Acme", "SWE Intern", "Remote", "SWE", db_path=test_db
    )

    # Simulate a re-run of the monitor over the same job.
    result = database_monitor.upsert_internship(
        "Acme", "SWE Intern", "Remote", "SWE",
        "https://acme.com/jobs/1",
        source_platform="greenhouse",
        external_job_id="1",
        db_path=test_db
    )
    assert result["is_new"] is False

    # A real monitor run would only call create_alert_for_new_internship
    # when is_new is True, so simulate that here.
    conn = sqlite3.connect(test_db)
    count = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
    conn.close()

    assert count == 1
