from datetime import date, timedelta

import database
from validators import get_blood_type, get_date, get_int, get_yes_no


def add_blood_unit():
    """Record a donated blood unit."""

    blood_type = get_blood_type("Blood type: ")

    collection = get_date(
        "Collection date (YYYY-MM-DD), or Enter for today: ",
        allow_blank=True
    )

    if collection is None:
        collection = date.today().isoformat()

    collection_obj = date.fromisoformat(collection)
    expiry = (collection_obj + timedelta(days=42)).isoformat()

    donor_id = None

    if get_yes_no("Link to a donor?"):
        donor_id = get_int("Donor ID: ", minimum=1)

        conn = database.get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT donor_id FROM donors WHERE donor_id=?",
            (donor_id,)
        )

        if cur.fetchone() is None:
            print("Donor not found. Blood unit will not be linked.")
            donor_id = None
        else:
            cur.execute(
                """
                UPDATE donors
                SET last_donation_date=?
                WHERE donor_id=?
                """,
                (collection, donor_id)
            )

        conn.commit()
        conn.close()

    conn = database.get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO blood_units
        (blood_type, collection_date, expiry_date, status, donor_id)
        VALUES (?, ?, ?, 'available', ?)
        """,
        (blood_type, collection, expiry, donor_id)
    )

    unit_id = cur.lastrowid

    conn.commit()
    conn.close()

    print(f"Unit #{unit_id} ({blood_type}) added. Expires on {expiry}.")


def view_stock():
    """Display available blood units."""

    today = date.today().isoformat()

    conn = database.get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT blood_type, COUNT(*)
        FROM blood_units
        WHERE status='available'
          AND expiry_date>=?
        GROUP BY blood_type
        ORDER BY blood_type
        """,
        (today,)
    )

    rows = cur.fetchall()

    conn.close()

    if not rows:
        print("No blood units in stock.")
        return

    print("\nBlood Type | Units Available")
    print("----------------------------")

    for blood_type, count in rows:
        print(f"{blood_type:<10} {count}")


def check_expiring_units():
    """Show units expiring within seven days."""

    today = date.today().isoformat()
    limit = (date.today() + timedelta(days=7)).isoformat()

    conn = database.get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT unit_id, blood_type, expiry_date
        FROM blood_units
        WHERE status='available'
          AND expiry_date>=?
          AND expiry_date<=?
        ORDER BY expiry_date
        """,
        (today, limit)
    )

    rows = cur.fetchall()

    conn.close()

    if not rows:
        print("No units are expiring within 7 days.")
        return

    print("\nWARNING: The following units expire soon:")

    for unit_id, blood_type, expiry in rows:
        print(
            f"Unit #{unit_id} ({blood_type}) expires on {expiry}"
        )


def remove_expired_units():
    """Mark expired units."""

    today = date.today().isoformat()

    conn = database.get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE blood_units
        SET status='expired'
        WHERE status='available'
          AND expiry_date < ?
        """,
        (today,)
    )

    conn.commit()

    count = cur.rowcount

    conn.close()

    if count:
        print(f"{count} expired unit(s) removed from stock.")
    else:
        print("No expired units found - stock is clean.")
