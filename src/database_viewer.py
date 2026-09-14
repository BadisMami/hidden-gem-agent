import sqlite3
import pandas as pd


conn = sqlite3.connect(
    "database/internship_agent.db"
)

print("\nCOMPANIES\n")
print(
    pd.read_sql(
        "SELECT * FROM companies",
        conn
    ).head()
)

print("\nUSERS\n")
print(
    pd.read_sql(
        "SELECT * FROM users",
        conn
    )
)

print("\nINTERNSHIPS\n")
print(
    pd.read_sql(
        "SELECT * FROM internships",
        conn
    )
)

conn.close()