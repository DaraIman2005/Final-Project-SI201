import requests
import sqlite3

DB_NAME = "project.db"
TICKETMASTER_API_KEY = "1wTwzG4mA9DsQFFEm1A5Q0cBfEGIRxhA"

ARTISTS = [
    "Taylor Swift",
    "Drake",
    "Kendrick Lamar",
    "Billie Eilish"
]

def create_table():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        event_id TEXT PRIMARY KEY,
        artist TEXT,
        venue TEXT,
        city TEXT
    )
""")

    conn.commit()
    conn.close()


def store_events(limit=25):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    inserted = 0

    for artist in ARTISTS:
        response = requests.get(
            "https://app.ticketmaster.com/discovery/v2/events.json",
            params={
                "apikey": TICKETMASTER_API_KEY,
                "keyword": artist,
                "size": 50
            }
        ).json()

        if "_embedded" not in response:
            continue

        for event in response["_embedded"]["events"]:
            if inserted >= limit:
                break

            venue = event["_embedded"]["venues"][0]
            cur.execute("""
                INSERT OR IGNORE INTO events
                VALUES (?, ?, ?, ?)
            """, (
                event["id"],
                artist,
                venue["name"],
                venue["city"]["name"]
            ))

            if cur.rowcount > 0:
                inserted += 1

    conn.commit()
    conn.close()
    print(f"Inserted {inserted} Ticketmaster events.")


if __name__ == "__main__":
    create_table()
    store_events(limit=25)