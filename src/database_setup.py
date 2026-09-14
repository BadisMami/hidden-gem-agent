import sqlite3


def create_database():

    conn = sqlite3.connect(
        "database/internship_agent.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        industry TEXT,
        career_url TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        major TEXT,
        interests TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS internships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        title TEXT,
        location TEXT,
        role_type TEXT,
        application_url TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        title TEXT,
        location TEXT,
        matched_users TEXT
    )
    """)

    conn.commit()
    conn.close()

    print("Database Created Successfully")


if __name__ == "__main__":
    create_database()