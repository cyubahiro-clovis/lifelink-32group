#!/usr/bin/python3
"""
database.py: The database layer for LifeLink.
Owner: Clovis

Holds two classes:
  Database     - owns the SQLite file, gives connections, creates the tables.
  BaseManager  - the parent class every feature manager inherits from,
                 so they all share the same database object.

The tables match the architecture diagram in our PLP-1 document:
donors | blood_units | blood_requests | issued_units (distributions) | staff

The staff table also stores each user's ROLE, so the system knows who is
allowed to do what: an administrator can approve requests and delete
records, while a technician does the day-to-day data entry.
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
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'technician'
            )
        """)

        self._add_role_column_if_missing(cur)
        self._create_default_accounts(cur)

        conn.commit()
        conn.close()

    def _add_role_column_if_missing(self, cur):
        """
        If someone still has a database created before we added roles, add the
        role column instead of failing. This keeps old databases working.
        """
        cur.execute("PRAGMA table_info(staff)")
        columns = [row[1] for row in cur.fetchall()]
        if "role" not in columns:
            cur.execute(
                "ALTER TABLE staff ADD COLUMN role TEXT NOT NULL "
                "DEFAULT 'technician'"
            )
            cur.execute("UPDATE staff SET role = 'admin' WHERE username = 'admin'")

    def _create_default_accounts(self, cur):
        """Create the two demo accounts once: one administrator, one technician."""
        accounts = [
            ("admin", "blood2026", "admin"),
            ("tech", "blood2026", "technician"),
        ]
        for username, password, role in accounts:
            cur.execute(
                "SELECT COUNT(*) FROM staff WHERE username = ?", (username,))
            if cur.fetchone()[0] == 0:
                cur.execute(
                    "INSERT INTO staff (username, password, role) "
                    "VALUES (?, ?, ?)",
                    (username, password, role),
                )


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
