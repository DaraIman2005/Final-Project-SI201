import sqlite3
import matplotlib.pyplot as plt

DB_NAME = "project.db"
OUTPUT_TXT = "calculated_results.txt"

def fetch_itunes_song_counts(conn):
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

def fetch_web_claimed_sales(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT artist_name, claimed_sales
        FROM web_artists
    """)
    rows = cur.fetchall()
    result = []
    for name, text in rows:
        lower = text.lower()
        num_str = "".join(ch for ch in text if ch.isdigit())
        if not num_str:
            continue
        value = int(num_str)
        if "million" in lower:
            value = value * 1000000
        elif "billion" in lower:
            value = value * 1000000000
        result.append((name, value))
    return result

def write_results_to_file(song_counts, event_counts, web_sales, filename=OUTPUT_TXT):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Calculated Results (iTunes + Ticketmaster + Web)\n")
        f.write("===============================================\n\n")
        f.write("1) iTunes Song Counts per Artist\n")
        for name, count in song_counts:
            f.write(f"- {name}: {count} songs\n")
        f.write("\n")
        f.write("2) Ticketmaster Event Counts per Artist\n")
        for name, count in event_counts:
            f.write(f"- {name}: {count} events\n")
        f.write("\n")
        f.write("3) Web Claimed Sales per Artist (approx)\n")
        for name, value in web_sales:
            f.write(f"- {name}: {value} units (approx)\n")
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
    web_sales = fetch_web_claimed_sales(conn)
    conn.close()
    write_results_to_file(song_counts, event_counts, web_sales)
    print(f"Wrote calculations to {OUTPUT_TXT}")
    if song_counts:
        plot_bar(song_counts, "iTunes Songs Per Artist", "Number of Songs")
    if event_counts:
        plot_bar(event_counts, "Ticketmaster Events Per Artist", "Number of Events")
    if web_sales:
        plot_bar(web_sales, "Claimed Sales Per Artist (Wikipedia)", "Claimed Sales (approx)")

if __name__ == "__main__":
    main()
