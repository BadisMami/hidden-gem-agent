import sqlite3
import pandas as pd

DB_PATH = "database/internship_agent.db"


def find_internships(role):

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT *
    FROM internships
    WHERE LOWER(role_type)=LOWER(?)
    """

    results = pd.read_sql(
        query,
        conn,
        params=(role,)
    )

    conn.close()

    return results


if __name__ == "__main__":

    internships = find_internships(
        "SWE"
    )

    print(internships)