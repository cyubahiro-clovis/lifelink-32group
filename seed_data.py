#!/usr/bin/python3
"""
seed_data.py - Fills the database with sample data for testing and the demo.
Owner: Nziza.

Run it once on a fresh database:   python3 seed_data.py
To start over:  delete lifelink.db, then run this again.

Demo moments built in on purpose:
  - one unit that expires in 2 days  -> the expiry warning fires live
  - one unit that already expired    -> "Remove expired units" shows a result
  - O- units (universal donor)       -> compatibility matching looks impressive
  - donors who last gave 90+ days ago-> the eligible donor list is not empty
All data is invented for this student project. No real patient or donor data.
"""

from datetime import date, timedelta

from database import Database

SHELF_LIFE_DAYS = 42


def add_donor(cur, name, blood_type, contact, days_since_last_donation=None):
    last = None
    if days_since_last_donation is not None:
        last = (date.today() - timedelta(days=days_since_last_donation)).isoformat()
    cur.execute(
        "INSERT INTO donors (name, blood_type, contact, last_donation_date) "
        "VALUES (?, ?, ?, ?)",
        (name, blood_type, contact, last),
    )
    return cur.lastrowid


def add_unit(cur, blood_type, collected_days_ago, donor_id=None):
    collection = date.today() - timedelta(days=collected_days_ago)
    expiry = collection + timedelta(days=SHELF_LIFE_DAYS)
    cur.execute(
        "INSERT INTO blood_units (blood_type, quantity_ml, collection_date, "
        "expiry_date, status, donor_id) VALUES (?, 450, ?, ?, 'available', ?)",
        (blood_type, collection.isoformat(), expiry.isoformat(), donor_id),
    )


def main():
    db = Database()
    db.create_tables()
    conn = db.get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM donors")
    if cur.fetchone()[0] > 0:
        print("The database already contains data - nothing was added.")
        print("To reload sample data: delete lifelink.db, then run this again.")
        conn.close()
        return

    # ---------------- donors ----------------
    d_aline = add_donor(cur, "Aline Uwase", "O-", "0788111222", 120)
    d_eric = add_donor(cur, "Eric Mugisha", "A+", "0788333444", 30)
    d_grace = add_donor(cur, "Grace Ingabire", "B+", "0788555666", 95)
    add_donor(cur, "Jean Bosco Habimana", "AB+", "0788777888", None)
    d_divine = add_donor(cur, "Divine Umutoni", "O+", "0788999000", 200)
    add_donor(cur, "Patrick Nkurunziza", "A-", "0788121314", 10)
    d_sandrine = add_donor(cur, "Sandrine Keza", "B-", "0788151617", 180)
    add_donor(cur, "Kevin Iradukunda", "AB-", "0788181920", 100)

    # ---------------- blood units ----------------
    add_unit(cur, "O-", 5, d_aline)      # universal donor unit
    add_unit(cur, "O-", 20)
    add_unit(cur, "A+", 10, d_eric)
    add_unit(cur, "A+", 25)
    add_unit(cur, "A+", 40)              # expires in 2 days -> live warning
    add_unit(cur, "B+", 3, d_grace)
    add_unit(cur, "B+", 15)
    add_unit(cur, "O+", 8, d_divine)
    add_unit(cur, "O+", 18)
    add_unit(cur, "O+", 30)
    add_unit(cur, "AB+", 12)
    add_unit(cur, "B-", 22, d_sandrine)
    add_unit(cur, "A-", 45)              # already expired -> cleanup demo

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM donors")
    donors = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM blood_units")
    units = cur.fetchone()[0]
    conn.close()

    print("Sample data inserted: {} donors and {} blood units.".format(
        donors, units))
    print("Now run:  python3 main.py   (login: admin / blood2026)")


if __name__ == "__main__":
    main()

