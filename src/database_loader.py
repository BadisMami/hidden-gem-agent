import sqlite3
import pandas as pd


DB_PATH = "database/internship_agent.db"


def load_companies():

    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_csv(
        "data/companies.csv"
    )

    companies.to_sql(
        "companies",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    print("Companies loaded.")


def load_users():

    conn = sqlite3.connect(DB_PATH)

    users = pd.read_csv(
        "data/users.csv"
    )

    users.to_sql(
        "users",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    print("Users loaded.")


def load_internships():

    conn = sqlite3.connect(DB_PATH)

    internships = pd.read_csv(
        "data/internships.csv"
    )

    internships.to_sql(
        "internships",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    print("Internships loaded.")


if __name__ == "__main__":

    load_companies()
    load_users()
    load_internships()

    print(
        "\nDatabase population complete."
    )