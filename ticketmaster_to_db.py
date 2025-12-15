import requests
import sqlite3

DB_NAME = "project.db"

# Put your Ticketmaster API key here
TICKETMASTER_API_KEY = "PUT_API_KEY_HERE"

# Use the same artist names as your iTunes script so joins work cleanly
ARTISTS = [
    "Taylor Swift",
    "Drake",
    "Kendrick Lamar",
    "Billie Eilish"
]


def create_table():
    """
    Creates the Ticketmaster events table.
    IMPORTANT: event_id is TEXT because Ticketmaster IDs are strings.
    """
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
    """
    Fetches events from Ticketmaster for each artist and stores up to `limit` NEW rows per run.
    Uses INSERT OR IGNORE to prevent duplicates.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    inserted = 0

    for artist in ARTISTS:
        if inserted >= limit:
            break

        response = requests.get(
            "https://app.ticketmaster.com/discovery/v2/events.json",
            params={
                "apikey": TICKETMASTER_API_KEY,
                "keyword": artist,
                "size": 50
            },
            timeout=15
        )

        # If the request fails, skip that artist
        if response.status_code != 200:
            continue

        data = response.json()

        # If no events, skip
        if "_embedded" not in data or "events" not in data["_embedded"]:
            continue

        for event in data["_embedded"]["events"]:
            if inserted >= limit:
                break

            try:
                event_id = str(event["id"])  # ensure TEXT
                venue_info = event["_embedded"]["venues"][0]
                venue_name = venue_info.get("name", "Unknown Venue")
                city_name = venue_info.get("city", {}).get("name", "Unknown City")

                cur.execute("""
                    INSERT OR IGNORE INTO events
                    (event_id, artist, venue, city)
                    VALUES (?, ?, ?, ?)
                """, (event_id, artist, venue_name, city_name))

                if cur.rowcount > 0:
                    inserted += 1

            except (KeyError, IndexError, TypeError):
                continue

    conn.commit()
    conn.close()
    print(f"Inserted {inserted} Ticketmaster events.")


if __name__ == "__main__":
    create_table()
    store_events(limit=25)
