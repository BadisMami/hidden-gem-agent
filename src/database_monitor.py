import sqlite3
from datetime import datetime

from database_setup import DB_PATH, _compute_dedup_key
from role_classifier import is_target_role, is_grad_only
from database_alerts import save_alert


def upsert_internship(
    company,
    title,
    location,
    role_type,
    application_url,
    source_platform="legacy",
    external_job_id=None,
    db_path=DB_PATH
):
    """
    Insert a new internship, or refresh last_seen/is_active on an existing
    one. Uniqueness is determined by dedup_key:
      - source_platform + company + external_job_id, when an external id
        is available (e.g. Greenhouse job id)
      - company + title + location + application_url otherwise

    Returns a dict: {"is_new": bool, "dedup_key": str}
    """

    dedup_key = _compute_dedup_key(
        source_platform,
        company,
        title,
        location,
        application_url,
        external_job_id
    )

    now = datetime.now().isoformat()

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM internships WHERE dedup_key = ?",
        (dedup_key,)
    )

    existing = cursor.fetchone()

    if existing:

        cursor.execute(
            """
            UPDATE internships
            SET last_seen = ?,
                is_active = 1,
                role_type = ?,
                application_url = ?
            WHERE dedup_key = ?
            """,
            (now, role_type, application_url, dedup_key)
        )

        conn.commit()
        conn.close()

        return {"is_new": False, "dedup_key": dedup_key}

    cursor.execute(
        """
        INSERT INTO internships (
            external_job_id, company, title, location, role_type,
            application_url, source_platform, date_discovered,
            last_seen, is_active, dedup_key
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        """,
        (
            external_job_id, company, title, location, role_type,
            application_url, source_platform, now, now, dedup_key
        )
    )

    conn.commit()
    conn.close()

    return {"is_new": True, "dedup_key": dedup_key}


def create_alert_for_new_internship(
    company,
    title,
    location,
    role_type,
    application_url="",
    db_path=DB_PATH
):
    """
    Create an alert for a newly discovered internship if its role_type is
    one of my target roles (see role_classifier.TARGET_ROLES) and it
    isn't a PhD/Master's-only posting. Returns None otherwise.
    """

    if not is_target_role(role_type) or is_grad_only(title):
        return None

    save_alert(
        company,
        title,
        location,
        application_url=application_url,
        db_path=db_path
    )

    return {"role_type": role_type}
