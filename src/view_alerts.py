import sqlite3
import pandas as pd

DB_PATH = "database/internship_agent.db"

conn = sqlite3.connect(DB_PATH)

alerts = pd.read_sql(
    "SELECT * FROM alerts",
    conn
)

print(alerts)

conn.close()