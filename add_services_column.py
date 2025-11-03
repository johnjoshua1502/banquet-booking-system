import sqlite3

DB = "banquet.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

# Check whether column exists first (safe)
cur.execute("PRAGMA table_info(bookings)")
cols = [row[1] for row in cur.fetchall()]
if "services" not in cols:
    cur.execute("ALTER TABLE bookings ADD COLUMN services TEXT")
    print("Added column 'services' to bookings table.")
else:
    print("'services' column already exists.")

conn.commit()
conn.close()
