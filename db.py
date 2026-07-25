#!/usr/bin/python3
"""Shared SQLite connection helper for the LifeLink project.

Every module (donor.py, inventory.py, blood_requests.py, reports.py,
alerts.py) should import get_connection() from here so the whole
group works against the same database file and schema!!
"""
import os
import sqlite3

_HERE = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(_HERE, "lifelink.db")
SCHEMA_FILE = os.path.join(_HERE, "schema.sql")


def get_connection():
    """Return a sqlite3 connection with row access by column name."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables from schema.sql if they don't already exist."""
    conn = get_connection()
    with open(SCHEMA_FILE, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized at {}".format(DB_NAME))
