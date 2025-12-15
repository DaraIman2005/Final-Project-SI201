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
    cur.execute("DROP TABLE IF EXISTS events")
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
        if inserted >= limit:
            break
        response = requests.get(
            "https://app.ticketmaster.com/discovery/v2/events.json",
            params={"apikey": TICKETMASTER_API_KEY, "keyword": artist, "size": 50},
            timeout=15
        )
        if response.status_code != 200:
            continue
        data = response.json()
        if "_embedded" not in data or "events" not in data["_embedded"]:
            continue
        for event in data["_embedded"]["events"]:
            if inserted >= limit:
                break
            try:
                event_id = str(event["id"])
                venue = event["_embedded"]["venues"][0]
                venue_name = venue.get("name", "Unknown Venue")
                city_name = venue.get("city", {}).get("name", "Unknown City")
                cur.execute(
                    "INSERT OR IGNORE INTO events VALUES (?, ?, ?, ?)",
                    (event_id, artist, venue_name, city_name)
                )
                if cur.rowcount > 0:
                    inserted += 1
            except:
                continue
    conn.commit()
    conn.close()
    print(f"Inserted {inserted} Ticketmaster events.")

if __name__ == "__main__":
    create_table()
    store_events(limit=25)