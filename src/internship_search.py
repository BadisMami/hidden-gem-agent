import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "database/internship_agent.db"
)

keyword = input(
    "Enter keyword: "
)

query = """
SELECT *
FROM internships
WHERE title LIKE ?
"""

results = pd.read_sql(
    query,
    conn,
    params=(f"%{keyword}%",)
)

print(results)

conn.close()