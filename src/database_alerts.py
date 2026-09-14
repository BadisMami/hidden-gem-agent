import sqlite3
from datetime import datetime

DB_PATH = "database/internship_agent.db"


def save_alert(
    company,
    title,
    location,
    matched_users,
    match_score
):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO alerts (
        timestamp,
        company,
        title,
        location,
        matched_users,
        match_score
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        str(datetime.now()),
        company,
        title,
        location,
        ",".join(matched_users),
        match_score
    ))

    conn.commit()
    conn.close()

    print(
        f"Alert saved: {company}"
    )