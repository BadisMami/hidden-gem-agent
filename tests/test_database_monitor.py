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


def test_insert_new_internship(test_db):

    result = database_monitor.upsert_internship(
        "Acme", "SWE Intern", "Remote", "SWE",
        "https://acme.com/jobs/1",
        source_platform="greenhouse",
        external_job_id="1",
        db_path=test_db
    )

    assert result["is_new"] is True

    conn = sqlite3.connect(test_db)
    count = conn.execute(
        "SELECT COUNT(*) FROM internships"
    ).fetchone()[0]
    conn.close()

    assert count == 1


def test_duplicate_insert_does_not_create_second_row(test_db):

    database_monitor.upsert_internship(
        "Acme", "SWE Intern", "Remote", "SWE",
        "https://acme.com/jobs/1",
        source_platform="greenhouse",
        external_job_id="1",
        db_path=test_db
    )

    result = database_monitor.upsert_internship(
        "Acme", "SWE Intern", "Remote", "SWE",
        "https://acme.com/jobs/1",
        source_platform="greenhouse",
        external_job_id="1",
        db_path=test_db
    )

    assert result["is_new"] is False

    conn = sqlite3.connect(test_db)
    count = conn.execute(
        "SELECT COUNT(*) FROM internships"
    ).fetchone()[0]
    conn.close()

    assert count == 1


def test_different_jobs_at_same_company_both_inserted(test_db):

    database_monitor.upsert_internship(
        "Acme", "SWE Intern", "Remote", "SWE",
        "https://acme.com/jobs/1",
        source_platform="greenhouse",
        external_job_id="1",
        db_path=test_db
    )

    database_monitor.upsert_internship(
        "Acme", "ML Intern", "Remote", "ML",
        "https://acme.com/jobs/2",
        source_platform="greenhouse",
        external_job_id="2",
        db_path=test_db
    )

    conn = sqlite3.connect(test_db)
    count = conn.execute(
        "SELECT COUNT(*) FROM internships"
    ).fetchone()[0]
    conn.close()

    assert count == 2


def test_repeated_run_creates_no_duplicate_rows(test_db):
    """Simulates re-running the monitor twice over the same job list."""

    jobs = [
        ("Acme", "SWE Intern", "Remote", "SWE",
         "https://acme.com/jobs/1", "1"),
        ("Acme", "ML Intern", "Remote", "ML",
         "https://acme.com/jobs/2", "2"),
    ]

    for _ in range(2):

        for company, title, location, role_type, url, job_id in jobs:

            database_monitor.upsert_internship(
                company, title, location, role_type, url,
                source_platform="greenhouse",
                external_job_id=job_id,
                db_path=test_db
            )

    conn = sqlite3.connect(test_db)
    count = conn.execute(
        "SELECT COUNT(*) FROM internships"
    ).fetchone()[0]
    conn.close()

    assert count == 2
