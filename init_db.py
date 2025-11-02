import sqlite3
from werkzeug.security import generate_password_hash
import os

DB = "banquet.db"

def ensure_tables_and_seed():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # create users table if missing
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, is_admin INTEGER DEFAULT 0)")

    # create halls table if missing (image_url added)
    c.execute("CREATE TABLE IF NOT EXISTS halls (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, capacity INTEGER, price REAL, description TEXT, image_url TEXT)")

    # create bookings table if missing
    c.execute("CREATE TABLE IF NOT EXISTS bookings (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, hall_id INTEGER NOT NULL, date TEXT NOT NULL, time_slot TEXT NOT NULL, guests INTEGER, status TEXT DEFAULT 'Pending', created_at TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(hall_id) REFERENCES halls(id))")

    # ensure admin exists
    c.execute("SELECT COUNT(*) FROM users WHERE is_admin=1")
    if c.fetchone()[0] == 0:
        admin_pass = generate_password_hash("admin123")
        c.execute("INSERT INTO users (name, email, password_hash, is_admin) VALUES (?, ?, ?, ?)", ("Admin", "admin@example.com", admin_pass, 1))

    # ensure image_url column exists (for older DBs)
    c.execute("PRAGMA table_info(halls)")
    cols = [r[1] for r in c.fetchall()]
    if 'image_url' not in cols:
        print('Adding image_url column to halls table...')
        c.execute("ALTER TABLE halls ADD COLUMN image_url TEXT")

    # seed default halls only if none exist
    c.execute("SELECT COUNT(*) FROM halls")
    if c.fetchone()[0] == 0:
        halls = [
            ("Grand Hall", 300, 25000.0, "Our largest and most prestigious hall...", "images/grand_hall.jpg"),
            ("Silver Hall", 120, 12000.0, "An elegant medium-sized hall...", "images/silver_hall.jpg"),
            ("Rose Hall", 60, 6000.0, "A charming and cozy space...", "images/rose_hall.jpg")
        ]
        c.executemany("INSERT INTO halls (name, capacity, price, description, image_url) VALUES (?, ?, ?, ?, ?)", halls)

    conn.commit()
    conn.close()
    print("Database ensured and seeded if needed:", DB)


if __name__ == '__main__':
    ensure_tables_and_seed()