import pandas as pd

from database_setup import DB_PATH, create_database
from database_monitor import upsert_internship
from url_utils import clean_url


def load_companies(db_path=DB_PATH):
    """
    Reference/reseed the companies table from CSV. Safe to re-run -
    companies.csv is seed/reference data, not live-discovered data.
    """

    import sqlite3

    conn = sqlite3.connect(db_path)

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


def load_users(db_path=DB_PATH):
    """
    Reference/reseed the users table from CSV. Safe to re-run -
    users.csv is reference data, not live-discovered data.
    """

    import sqlite3

    conn = sqlite3.connect(db_path)

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


def load_internships(db_path=DB_PATH):
    """
    Seed internships from CSV using the dedup-aware upsert, rather than
    wholesale replacing the table (which would wipe out live-discovered
    data and the SQLite-native schema). Safe to re-run - existing rows
    are refreshed, not duplicated.
    """

    internships = pd.read_csv(
        "data/internships.csv"
    )

    inserted = 0
    updated = 0

    for _, row in internships.iterrows():

        result = upsert_internship(
            company=row["company"],
            title=row["title"],
            location=row.get("location", ""),
            role_type=row.get("role_type", "Other"),
            application_url=clean_url(row.get("application_url", "")),
            source_platform=row.get("source_platform", "csv-seed"),
            external_job_id=row.get("external_job_id") or None,
            db_path=db_path
        )

        if result["is_new"]:
            inserted += 1
        else:
            updated += 1

    print(
        f"Internships loaded: {inserted} new, {updated} already present."
    )


if __name__ == "__main__":

    create_database()

    load_companies()
    load_users()
    load_internships()

    print(
        "\nDatabase population complete."
    )