import sqlite3
import matplotlib.pyplot as plt
from collections import defaultdict

DB_NAME = "project.db"

def get_daily_activity():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            substr(e.created_at, 1, 10) AS date,
            COUNT(e.event_id),
            w.precipitation
        FROM events e
        JOIN weather w ON substr(e.created_at, 1, 10) = w.date
        GROUP BY date
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


def plot_events_over_time(data):
    dates = [row[0] for row in data]
    counts = [row[1] for row in data]

    plt.figure()
    plt.plot(dates, counts)
    plt.xticks(rotation=45)
    plt.title("GitHub Events Per Day")
    plt.tight_layout()
    plt.show()


def plot_precip_vs_events(data):
    precipitation = [row[2] for row in data]
    counts = [row[1] for row in data]

    plt.figure()
    plt.scatter(precipitation, counts)
    plt.xlabel("Precipitation")
    plt.ylabel("GitHub Events")
    plt.title("Precipitation vs GitHub Activity")
    plt.show()


if __name__ == "__main__":
    data = get_daily_activity()
    plot_events_over_time(data)
    plot_precip_vs_events(data)
