import sqlite3
from datetime import datetime

from database_setup import DB_PATH, _compute_dedup_key
from user_matcher import find_matching_users
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
    db_path=DB_PATH
):
    """
    Create an alert for a newly discovered internship, matched against
    users' declared interests (role_type). match_score is the number of
    matched users - resume-based scoring requires a per-user stored
    resume, which this schema does not track.
    """

    matched_users = find_matching_users(role_type)

    if not matched_users:
        return None

    match_score = len(matched_users)

    save_alert(
        company,
        title,
        location,
        matched_users,
        match_score,
        db_path=db_path
    )

    return {
        "matched_users": matched_users,
        "match_score": match_score
    }


if __name__ == "__main__":

    result = upsert_internship(
        "Scale AI",
        "AI Platform Engineering Intern",
        "San Francisco CA",
        "ML",
        "https://scale.com/careers",
        source_platform="legacy"
    )

    print(result)

    if result["is_new"]:

        alert = create_alert_for_new_internship(
            "Scale AI",
            "AI Platform Engineering Intern",
            "San Francisco CA",
            "ML"
        )

        print(alert)
