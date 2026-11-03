"""
Database management for Smart Campus Lost & Found Matcher.
Uses SQLite for lightweight, serverless persistence.
"""

import sqlite3
import os
from datetime import datetime

DATABASE_NAME = os.environ.get("DATABASE_NAME", "campus_lost_found.db")

def get_db_connection(db_path=None):
    """Establishes and returns a database connection with dict-like row access."""
    if db_path is None:
        db_path = DATABASE_NAME
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=None, seed_sample_data=True):
    """Initializes the database schema and seeds initial data if requested."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL CHECK(item_type IN ('lost', 'found')),
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            colour TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT NOT NULL,
            contact_info TEXT,
            status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'Returned')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    if seed_sample_data:
        cursor.execute("SELECT COUNT(*) AS count FROM items")
        count = cursor.fetchone()["count"]
        if count == 0:
            sample_items = [
                (
                    "lost",
                    "Blue Hydro Flask Water Bottle",
                    "Personal Accessories",
                    "Pacific Blue",
                    "Campus Library 2nd Floor Study Desk",
                    "32oz wide mouth Pacific Blue water bottle with stickers from NASA and CS Club on it. Minor dent on bottom.",
                    "student1@campus.edu",
                    "Active",
                    "2025-05-10 10:15:00"
                ),
                (
                    "found",
                    "Blue Water Bottle with Stickers",
                    "Personal Accessories",
                    "Blue",
                    "Library Main Hall near Printers",
                    "Navy or Pacific blue insulated stainless steel water bottle. Has university science and space stickers.",
                    "frontdesk@campus.edu",
                    "Active",
                    "2025-05-10 14:30:00"
                ),
                (
                    "lost",
                    "MacBook Pro 14 M2 Silver",
                    "Electronics",
                    "Silver",
                    "Engineering Hall Room 302",
                    "Silver Apple MacBook Pro laptop inside a dark grey felt sleeve. Left during CS301 lab on Tuesday morning.",
                    "coder@campus.edu",
                    "Active",
                    "2025-05-09 11:20:00"
                ),
                (
                    "found",
                    "Apple Laptop in Grey Case",
                    "Electronics",
                    "Silver / Grey",
                    "Engineering Building Lab 302",
                    "Found a silver MacBook in dark grey protective sleeve on desk row 3 after morning lecture.",
                    "eng-office@campus.edu",
                    "Active",
                    "2025-05-09 12:45:00"
                ),
                (
                    "lost",
                    "Black Leather Trifold Wallet",
                    "Wallets & IDs",
                    "Black",
                    "Student Union Food Court",
                    "Black genuine leather wallet containing Student ID card and bus transit pass.",
                    "555-0199",
                    "Active",
                    "2025-05-08 13:00:00"
                ),
                (
                    "found",
                    "Black Leather Wallet",
                    "Wallets & IDs",
                    "Black",
                    "Cafeteria Table 12",
                    "Mens black trifold wallet with campus card left behind near trash station.",
                    "dining-lostfound@campus.edu",
                    "Returned",
                    "2025-05-07 15:00:00"
                ),
                (
                    "lost",
                    "Sony WH-1000XM4 Noise Cancelling Headphones",
                    "Electronics",
                    "Black",
                    "Campus Gym Locker Room",
                    "Over-ear matte black wireless headphones in hard carrying case with audio cable.",
                    "alex@campus.edu",
                    "Active",
                    "2025-05-11 08:30:00"
                ),
                (
                    "found",
                    "Black Over-Ear Wireless Headphones",
                    "Electronics",
                    "Black",
                    "Athletic Center Front Desk",
                    "Black Sony wireless headphones handed in by gym staff from bench area.",
                    "gym-desk@campus.edu",
                    "Active",
                    "2025-05-11 10:00:00"
                ),
                (
                    "lost",
                    "Calculus 3 Early Transcendentals Textbook",
                    "Books & Notes",
                    "Blue / White",
                    "Science Lecture Hall A",
                    "Hardcover Stewart Calculus 9th edition with highlighted chapter 14 notes inside.",
                    "mathlover@campus.edu",
                    "Active",
                    "2025-05-06 16:00:00"
                )
            ]

            cursor.executemany("""
                INSERT INTO items (
                    item_type, name, category, colour, location, description, contact_info, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_items)
            conn.commit()

    conn.close()

def get_all_items(item_type=None, status=None, search=None, category=None, db_path=None):
    """Fetches items with optional filtering and search."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    query = "SELECT * FROM items WHERE 1=1"
    params = []

    if item_type:
        query += " AND item_type = ?"
        params.append(item_type)
    if status:
        query += " AND status = ?"
        params.append(status)
    if category:
        query += " AND category = ?"
        params.append(category)
    if search:
        search_param = f"%{search.strip()}%"
        query += " AND (name LIKE ? OR description LIKE ? OR location LIKE ? OR colour LIKE ?)"
        params.extend([search_param, search_param, search_param, search_param])

    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    items = [dict(row) for row in rows]
    conn.close()
    return items

def get_item_by_id(item_id, db_path=None):
    """Fetches a single item by ID."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_item(item_data, db_path=None):
    """Inserts a new lost or found item."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO items (
            item_type, name, category, colour, location, description, contact_info, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item_data.get("item_type"),
        item_data.get("name"),
        item_data.get("category"),
        item_data.get("colour"),
        item_data.get("location"),
        item_data.get("description"),
        item_data.get("contact_info", ""),
        item_data.get("status", "Active"),
        now,
        now
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def update_item_status(item_id, status, db_path=None):
    """Updates the status of an item (e.g. Active or Returned)."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        UPDATE items
        SET status = ?, updated_at = ?
        WHERE id = ?
    """, (status, now, item_id))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated

def get_dashboard_stats(db_path=None):
    """Calculates statistics for the dashboard."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM items")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS lost_count FROM items WHERE item_type = 'lost'")
    lost_count = cursor.fetchone()["lost_count"]

    cursor.execute("SELECT COUNT(*) AS found_count FROM items WHERE item_type = 'found'")
    found_count = cursor.fetchone()["found_count"]

    cursor.execute("SELECT COUNT(*) AS active_count FROM items WHERE status = 'Active'")
    active_count = cursor.fetchone()["active_count"]

    cursor.execute("SELECT COUNT(*) AS returned_count FROM items WHERE status = 'Returned'")
    returned_count = cursor.fetchone()["returned_count"]

    conn.close()
    return {
        "total": total,
        "lost": lost_count,
        "found": found_count,
        "active": active_count,
        "returned": returned_count
    }

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully with sample data.")
