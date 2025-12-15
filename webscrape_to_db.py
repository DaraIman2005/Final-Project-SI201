import requests
import sqlite3
from bs4 import BeautifulSoup

DB_NAME = "project.db"

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
        CREATE TABLE IF NOT EXISTS web_artists (
            artist_name TEXT PRIMARY KEY,
            claimed_sales TEXT
        )
    """)
    conn.commit()
    conn.close()

def store_web_data():
    url = "https://en.wikipedia.org/wiki/List_of_best-selling_music_artists"
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        " AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/119.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers, timeout=20)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    inserted = 0

    tables = soup.find_all("table", class_="wikitable")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows[1:]:
            cells = row.find_all(["td", "th"])
            if len(cells) < 2:
                continue

            link = cells[0].find("a")
            if not link:
                continue

            name = link.get_text(strip=True)
            if name not in ARTISTS:
                continue

            claimed = cells[-1].get_text(" ", strip=True)

            cur.execute("""
                INSERT OR REPLACE INTO web_artists
                VALUES (?, ?)
            """, (name, claimed))

            inserted += 1

    conn.commit()
    conn.close()
    print(f"Inserted {inserted} web rows.")

if __name__ == "__main__":
    create_table()
    store_web_data()
