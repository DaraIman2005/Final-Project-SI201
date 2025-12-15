import sqlite3
import matplotlib.pyplot as plt

DB_NAME = "project.db"

def get_counts():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT a.name, COUNT(t.track_id)
        FROM artists a
        JOIN tracks t ON a.artist_id = t.artist_id
        GROUP BY a.name
    """)
    tracks = cur.fetchall()

    cur.execute("""
        SELECT artist, COUNT(event_id)
        FROM events
        GROUP BY artist
    """)
    events = cur.fetchall()

    conn.close()
    return tracks, events


def plot_bar(data, title, ylabel):
    labels = [x[0] for x in data]
    values = [x[1] for x in data]

    plt.figure()
    plt.bar(labels, values)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    tracks, events = get_counts()

    plot_bar(tracks, "Spotify Tracks per Artist", "Number of Tracks")
    plot_bar(events, "Ticketmaster Events per Artist", "Number of Events")