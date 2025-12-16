import sqlite3

conn = sqlite3.connect("project.db")
cur = conn.cursor()

tables = ["artists", "songs", "events", "web_artists"]

for table in tables:
    cur.execute(f"SELECT COUNT(*) FROM {table};")
    print(f"{table}: {cur.fetchone()[0]} rows")

conn.close()
