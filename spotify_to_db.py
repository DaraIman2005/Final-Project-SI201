import base64
import requests
import sqlite3

DB_NAME = "project.db"

SPOTIFY_CLIENT_ID = "PUT_CLIENT_ID_HERE"
SPOTIFY_CLIENT_SECRET = "PUT_CLIENT_SECRET_HERE"

ARTISTS = [
    "Taylor Swift",
    "Drake",
    "Kendrick Lamar",
    "Billie Eilish"
]

def get_token():
    auth = base64.b64encode(
        f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
    ).decode()

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {auth}"},
        data={"grant_type": "client_credentials"}
    )
    return response.json()["access_token"]


def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS artists (
            artist_id TEXT PRIMARY KEY,
            name TEXT UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            track_id TEXT PRIMARY KEY,
            artist_id TEXT,
            name TEXT,
            popularity INTEGER,
            FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
        )
    """)

    conn.commit()
    conn.close()


def store_spotify_data(limit=25):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    inserted = 0

    for artist_name in ARTISTS:
        search = requests.get(
            "https://api.spotify.com/v1/search",
            headers=headers,
            params={"q": artist_name, "type": "artist", "limit": 1}
        ).json()

        artist = search["artists"]["items"][0]
        artist_id = artist["id"]

        cur.execute(
            "INSERT OR IGNORE INTO artists VALUES (?, ?)",
            (artist_id, artist["name"])
        )

        top_tracks = requests.get(
            f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks",
            headers=headers,
            params={"market": "US"}
        ).json()["tracks"]

        for track in top_tracks:
            if inserted >= limit:
                break

            cur.execute("""
                INSERT OR IGNORE INTO tracks
                VALUES (?, ?, ?, ?)
            """, (
                track["id"],
                artist_id,
                track["name"],
                track["popularity"]
            ))

            if cur.rowcount > 0:
                inserted += 1

    conn.commit()
    conn.close()
    print(f"Inserted {inserted} Spotify tracks.")


if __name__ == "__main__":
    create_tables()
    store_spotify_data(limit=25)