#!/usr/bin/python3
"""
database.py: This Database layer for LifeLink.

Holds two classes:
  Database     - owns the SQLite file, gives connections, creates the tables.
  BaseManager  - parent class that every feature manager inherits from,
                 so they all share the same database object.

The tables match the architecture diagram in our PLP-1 document:
donors | blood_units | blood_requests | issued_units (distributions) | staff
"""

import os
import sqlite3


class Database:
    """Owns the SQLite database file and the schema."""

    def __init__(self, db_name="lifelink.db"):
        here = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(here, db_name)

    def get_connection(self):
        """Return a connection with foreign keys switched on."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def create_tables(self):
        """Create every table if it does not exist. Safe to run at each startup."""
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS donors (
                donor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                blood_type TEXT NOT NULL,
                contact TEXT,
                last_donation_date TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS blood_units (
                unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                blood_type TEXT NOT NULL,
                quantity_ml INTEGER NOT NULL DEFAULT 450,
                collection_date TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'available',
                donor_id INTEGER,
                FOREIGN KEY (donor_id) REFERENCES donors (donor_id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS blood_requests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                patient_blood_type TEXT NOT NULL,
                units_needed INTEGER NOT NULL,
                request_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS issued_units (
                issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                unit_id INTEGER NOT NULL,
                issue_date TEXT NOT NULL,
                FOREIGN KEY (request_id) REFERENCES blood_requests (request_id),
                FOREIGN KEY (unit_id) REFERENCES blood_units (unit_id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS staff (
                staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)

        cur.execute("SELECT COUNT(*) FROM staff")
        if cur.fetchone()[0] == 0:
            cur.execute(
                "INSERT INTO staff (username, password) VALUES (?, ?)",
                ("admin", "blood2026"),
            )

        conn.commit()
        conn.close()


class BaseManager:
    """Parent class for every feature manager (donors, inventory, etc.)."""

    def __init__(self, db):
        self.db = db

    def connect(self):
        """Shortcut so child classes can simply call self.connect()."""
        return self.db.get_connection()


if __name__ == "__main__":
    Database().create_tables()
    print("Database ready.")
 
