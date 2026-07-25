-- LifeLink Blood Bank Management System
-- This is shared schema. Everyone's .py files should query these same tables.

CREATE TABLE IF NOT EXISTS donors (
    donor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    blood_type TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    last_donation_date TEXT,
    is_eligible INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS blood_units (
    unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    blood_type TEXT NOT NULL,
    quantity_ml INTEGER NOT NULL,
    collection_date TEXT NOT NULL,
    expiry_date TEXT NOT NULL,
    status TEXT DEFAULT 'available'
);

CREATE TABLE IF NOT EXISTS donations (
    donation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    donor_id INTEGER NOT NULL,
    unit_id INTEGER,
    donation_date TEXT NOT NULL,
    FOREIGN KEY (donor_id) REFERENCES donors (donor_id),
    FOREIGN KEY (unit_id) REFERENCES blood_units (unit_id)
);

CREATE TABLE IF NOT EXISTS requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    requester_name TEXT NOT NULL,
    hospital TEXT,
    blood_type TEXT NOT NULL,
    quantity_ml INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',
    request_date TEXT NOT NULL
);
