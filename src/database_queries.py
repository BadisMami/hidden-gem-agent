import sqlite3
import pandas as pd

DB_PATH = "database/internship_agent.db"


def get_all_users():

    conn = sqlite3.connect(DB_PATH)

    users = pd.read_sql(
        "SELECT * FROM users",
        conn
    )

    conn.close()

    return users


def get_all_internships(active_only=True):

    conn = sqlite3.connect(DB_PATH)

    query = "SELECT * FROM internships"

    if active_only:
        query += " WHERE is_active = 1"

    internships = pd.read_sql(
        query,
        conn
    )

    conn.close()

    return internships


def get_all_companies():

    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_sql(
        "SELECT * FROM companies",
        conn
    )

    conn.close()

    return companies


if __name__ == "__main__":

    print("\nUSERS\n")
    print(get_all_users())

    print("\nINTERNSHIPS\n")
    print(get_all_internships().head())