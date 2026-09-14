import sqlite3

from intelligent_matcher import (
    calculate_match_score
)

from user_skills import (
    get_user_skills
)

from user_matcher import find_matching_users
from database_alerts import save_alert

DB_PATH = "database/internship_agent.db"


def internship_exists(company, title):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM internships
        WHERE company = ?
        AND title = ?
        """,
        (company, title)
    )

    count = cursor.fetchone()[0]

    conn.close()

    return count > 0


def add_internship(
    company,
    title,
    location,
    role_type,
    application_url
):

    if internship_exists(
        company,
        title
    ):

        print(
            f"Already exists: {company}"
        )

        return

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO internships (
            company,
            title,
            location,
            role_type,
            application_url
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            company,
            title,
            location,
            role_type,
            application_url
        )
    )

    conn.commit()
    conn.close()

    print(
        f"New internship added: {company}"
    )

    matched_users = find_matching_users(
        role_type
    )

    user_skills = get_user_skills()

    

    match_score = calculate_match_score(
        user_skills,
        title
    )

    save_alert(
        company,
        title,
        location,
        matched_users,
        match_score
    )

    print(
        f"Match Score: {match_score}"
    )

    print(
        f"Alert created for {matched_users}"
    )


if __name__ == "__main__":

    add_internship(
        "Scale AI",
        "AI Platform Engineering Intern",
        "San Francisco CA",
        "ML",
        "https://scale.com/careers"
    )