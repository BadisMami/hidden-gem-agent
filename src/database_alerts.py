import sqlite3
from datetime import datetime

from database_setup import DB_PATH


def save_alert(
    company,
    title,
    location,
    application_url="",
    db_path=DB_PATH
):
    """
    Save an alert as not-yet-texted. It's sent (and marked sent) by the
    next monitor run that falls inside the texting window.
    """

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO alerts (
        timestamp,
        company,
        title,
        location,
        application_url,
        sms_sent
    )
    VALUES (?, ?, ?, ?, ?, 0)
    """, (
        str(datetime.now()),
        company,
        title,
        location,
        application_url
    ))

    conn.commit()
    conn.close()

    print(
        f"Alert saved: {company}"
    )


def get_unsent_alerts(db_path=DB_PATH):

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT id, company, title, location, application_url
        FROM alerts
        WHERE sms_sent = 0
        ORDER BY id
        """
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def mark_alerts_sent(alert_ids, db_path=DB_PATH):

    conn = sqlite3.connect(db_path)

    conn.executemany(
        "UPDATE alerts SET sms_sent = 1 WHERE id = ?",
        [(alert_id,) for alert_id in alert_ids]
    )

    conn.commit()
    conn.close()
