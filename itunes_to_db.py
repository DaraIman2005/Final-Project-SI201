import requests
import sqlite3

DB_NAME = "project.db"

ARTISTS = [
    "Taylor Swift",
    "Drake",
    "Kendrick Lamar",
    "Billie Eilish"
]

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS artists (
            artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            track_id INTEGER PRIMARY KEY,
            artist_id INTEGER,
            track_name TEXT,
            popularity INTEGER,
            FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
        )
    """)

    conn.commit()
    conn.close()


def store_itunes_data(limit=25):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    inserted = 0

    for artist in ARTISTS:
        response = requests.get(
            "https://itunes.apple.com/search",
            params={
                "term": artist,
                "entity": "song",
                "limit": 50
            }
        ).json()

        cur.execute(
            "INSERT OR IGNORE INTO artists (name) VALUES (?)",
            (artist,)
        )

        cur.execute(
            "SELECT artist_id FROM artists WHERE name = ?",
            (artist,)
        )
        artist_id = cur.fetchone()[0]

        for song in response["results"]:
            if inserted >= limit:
                break

            cur.execute("""
                INSERT OR IGNORE INTO songs
                VALUES (?, ?, ?, ?)
            """, (
                song["trackId"],
                artist_id,
                song["trackName"],
                song.get("trackPrice", 0)
            ))

            if cur.rowcount > 0:
                inserted += 1

    conn.commit()
    conn.close()
    print(f"Inserted {inserted} iTunes tracks.")


if __name__ == "__main__":
    create_tables()
    store_itunes_data(limit=25)