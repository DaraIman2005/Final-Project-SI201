import sqlite3
import matplotlib.pyplot as plt

DB_NAME = "project.db"
OUTPUT_TXT = "calculated_results.txt"


def fetch_itunes_song_counts(conn):
    """
    Returns list of tuples: (artist_name, song_count)
    Uses a JOIN between artists and songs.
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT a.name, COUNT(s.track_id) AS song_count
        FROM artists a
        JOIN songs s ON a.artist_id = s.artist_id
        GROUP BY a.name
        ORDER BY song_count DESC
    """)
    return cur.fetchall()


def fetch_ticketmaster_event_counts(conn):
    """
    Returns list of tuples: (artist_name, event_count)
    Ticketmaster table stores artist as text, so we normalize using LOWER() join to artists.name.
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT a.name, COUNT(e.event_id) AS event_count
        FROM artists a
        LEFT JOIN events e
            ON LOWER(e.artist) = LOWER(a.name)
        GROUP BY a.name
        ORDER BY event_count DESC
    """)
    return cur.fetchall()


def fetch_avg_song_price(conn):
    """
    Returns list of tuples: (artist_name, avg_price)
    (Note: iTunes API gives trackPrice; we stored it in 'popularity' column in songs table.)
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT a.name, ROUND(AVG(s.popularity), 2) AS avg_price
        FROM artists a
        JOIN songs s ON a.artist_id = s.artist_id
        GROUP BY a.name
        ORDER BY avg_price DESC
    """)
    return cur.fetchall()


def write_results_to_file(song_counts, event_counts, avg_prices, filename=OUTPUT_TXT):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Calculated Results (iTunes + Ticketmaster)\n")
        f.write("========================================\n\n")

        f.write("1) iTunes Song Counts per Artist\n")
        for name, count in song_counts:
            f.write(f"- {name}: {count} songs\n")
        f.write("\n")

        f.write("2) Ticketmaster Event Counts per Artist\n")
        for name, count in event_counts:
            f.write(f"- {name}: {count} events\n")
        f.write("\n")

        f.write("3) Average iTunes Track Price per Artist\n")
        for name, avg in avg_prices:
            f.write(f"- {name}: ${avg}\n")
        f.write("\n")


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


def main():
    conn = sqlite3.connect(DB_NAME)

    song_counts = fetch_itunes_song_counts(conn)
    event_counts = fetch_ticketmaster_event_counts(conn)
    avg_prices = fetch_avg_song_price(conn)

    conn.close()

    write_results_to_file(song_counts, event_counts, avg_prices)
    print(f"Wrote calculations to {OUTPUT_TXT}")

    plot_bar(song_counts, "iTunes Songs Per Artist", "Number of Songs")

    plot_bar(event_counts, "Ticketmaster Events Per Artist", "Number of Events")


if __name__ == "__main__":
    main()