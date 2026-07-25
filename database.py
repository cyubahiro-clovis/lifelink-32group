#!/usr/bin/python3
"""
This database.py is a database connection and table creation for LifeLink.
Everyone imports this and should be changed after telling the team.

Tables match our PLP-1 architecture diagram:
    donors | Blood_units (blood_inventory) | blood_requests
    """

    import sqlite3

    DB_NAME = "lifelink.db"

    def get_connectio():
        """Return a connection to the LifeLink database with foreign keys ON."""
        conn = sqlite3.connect(DB_NAME)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


    def create_tables():
        """Create all tables if they do not exist yet. Safe to call at every startup."""
        conn = get _connection()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS donors (
                donor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                blood_type TEXT NOT NULL,
                contact TEX,
                last_donation_date TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS blood_requests (
                unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                blood_type TEXT NOT NULL,
                collection_date TEXT NOT NULL,
                expiry_date TEXT NULL,
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
        conn.commit()
        conn.close()
