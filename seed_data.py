#!/usr/bin/python3
"""Populate the LifeLink database with sample data for demos/testing."""
import random
from datetime import date, timedelta

from db import get_connection, init_db

BLOOD_TYPES = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]

DONOR_SAMPLES = [
    ("Aline Uwase", "O+", "0788111222", "aline.u@example.com"),
    ("Eric Niyonzima", "A-", "0788222333", "eric.n@example.com"),
    ("Grace Mukamana", "B+", "0788333444", "grace.m@example.com"),
    ("Jean Bosco", "AB+", "0788444555", "jean.b@example.com"),
    ("Diane Ingabire", "O-", "0788555666", "diane.i@example.com"),
    ("Patrick Habimana", "A+", "0788666777", "patrick.h@example.com"),
    ("Solange Umutoni", "B-", "0788777888", "solange.u@example.com"),
    ("Emmanuel Rugamba", "AB-", "0788888999", "emmanuel.r@example.com"),
]

HOSPITALS = [
    "King Faisal Hospital",
    "CHUK",
    "Rwanda Military Hospital",
    "Kibagabaga Hospital",
    "Nyamata District Hospital",
]

REQUESTERS = ["Dr. Kamanzi", "Dr. Uwimana", "Dr. Mugisha", "Dr. Keza"]
STATUSES = ["pending", "approved", "rejected"]
SHELF_LIFE_DAYS = 42


def seed_donors(conn):
    """Insert sample donors."""
    cur = conn.cursor()
    for name, blood_type, phone, email in DONOR_SAMPLES:
        last_donation = date.today() - timedelta(days=random.randint(10, 200))
        cur.execute(
            "INSERT INTO donors (full_name, blood_type, phone, email, "
            "last_donation_date, is_eligible) VALUES (?, ?, ?, ?, ?, ?)",
            (name, blood_type, phone, email, last_donation.isoformat(), 1),
        )
    conn.commit()


def seed_blood_units(conn, count=20):
    """Insert sample blood units, some already expired for testing."""
    cur = conn.cursor()
    for _ in range(count):
        blood_type = random.choice(BLOOD_TYPES)
        collected = date.today() - timedelta(days=random.randint(0, 60))
        expiry = collected + timedelta(days=SHELF_LIFE_DAYS)
        status = "expired" if expiry < date.today() else "available"
        cur.execute(
            "INSERT INTO blood_units (blood_type, quantity_ml, "
            "collection_date, expiry_date, status) "
            "VALUES (?, ?, ?, ?, ?)",
            (blood_type, 450, collected.isoformat(),
             expiry.isoformat(), status),
        )
    conn.commit()


def seed_donations(conn):
    """Link each donor to a donated unit."""
    cur = conn.cursor()
    donor_ids = [r[0] for r in cur.execute("SELECT donor_id FROM donors")]
    unit_ids = [r[0] for r in cur.execute("SELECT unit_id FROM blood_units")]
    for donor_id in donor_ids:
        unit_id = random.choice(unit_ids)
        donation_date = date.today() - timedelta(days=random.randint(0, 90))
        cur.execute(
            "INSERT INTO donations (donor_id, unit_id, donation_date) "
            "VALUES (?, ?, ?)",
            (donor_id, unit_id, donation_date.isoformat()),
        )
    conn.commit()


def seed_requests(conn, count=10):
    """Insert sample hospital blood requests."""
    cur = conn.cursor()
    for _ in range(count):
        req_date = date.today() - timedelta(days=random.randint(0, 30))
        cur.execute(
            "INSERT INTO requests (requester_name, hospital, blood_type, "
            "quantity_ml, status, request_date) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                random.choice(REQUESTERS),
                random.choice(HOSPITALS),
                random.choice(BLOOD_TYPES),
                random.choice([450, 900, 1350]),
                random.choice(STATUSES),
                req_date.isoformat(),
            ),
        )
    conn.commit()


def run_seed():
    """Initialize the database and load all sample data."""
    init_db()
    conn = get_connection()
    seed_donors(conn)
    seed_blood_units(conn)
    seed_donations(conn)
    seed_requests(conn)
    conn.close()
    print("Seed data inserted into {}".format("lifelink.db"))


if __name__ == "__main__":
    run_seed()
