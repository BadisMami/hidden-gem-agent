import sqlite3
import pandas as pd

DB_PATH = "database/internship_agent.db"


def show_alerts():

    conn = sqlite3.connect(DB_PATH)

    alerts = pd.read_sql(
        """
        SELECT *
        FROM alerts
        ORDER BY id DESC
        """,
        conn
    )

    conn.close()

    print("\n===== ALERT DASHBOARD =====\n")

    print(
    alerts[
        [
            "company",
            "title",
            "matched_users",
            "match_score"
        ]
    ]
)


if __name__ == "__main__":
    show_alerts()