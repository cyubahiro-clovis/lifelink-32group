#!/usr/bin/python3
"""
blood_bank.py - Unified Blood Bank Management System.

Combines database setup, input validation, blood request handling,
and the main CLI menu loop into a single file.
"""

from datetime import date
import os
import sqlite3

# ==============================================================================
# 1. DATABASE & SCHEMA MODULE
# ==============================================================================

DB_FILENAME = "blood_bank.db"


def get_connection():
    """Return a connection to the shared SQLite database.

    Creates the database file and its tables the first time it's called,
    if they don't already exist.
    """
    is_new_db = not os.path.exists(DB_FILENAME)
    conn = sqlite3.connect(DB_FILENAME)

    if is_new_db:
        _create_tables(conn)

    return conn


def _create_tables(conn):
    """Create the blood_units and blood_requests tables."""
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS blood_units (
            unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            blood_type TEXT NOT NULL,
            expiry_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'available'
        )
    """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS blood_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            patient_blood_type TEXT NOT NULL,
            units_needed INTEGER NOT NULL,
            request_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending'
        )
    """
    )

    conn.commit()


def seed_sample_data():
    """Insert sample blood units for testing/demo. Safe to call multiple times."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM blood_units")
    count = cur.fetchone()[0]

    if count == 0:
        sample_units = [
            ("O-", "2026-08-15"),
            ("O-", "2026-09-01"),
            ("A+", "2026-08-20"),
            ("A+", "2026-10-05"),
            ("B+", "2026-08-10"),
            ("AB+", "2026-11-01"),
            ("O+", "2026-08-25"),
            ("O+", "2026-09-15"),
        ]
        cur.executemany(
            "INSERT INTO blood_units (blood_type, expiry_date) VALUES (?, ?)",
            sample_units,
        )
        conn.commit()

    conn.close()


# ==============================================================================
# 2. VALIDATORS MODULE
# ==============================================================================

VALID_BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]


def get_nonempty(prompt):
    """Keep asking until the user enters a non-empty string."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty. Please try again.")


def get_blood_type(prompt):
    """Keep asking until the user enters a valid blood type."""
    while True:
        value = input(prompt).strip().upper()
        if value in VALID_BLOOD_TYPES:
            return value
        print(
            "Invalid blood type. Valid options are: {}".format(
                ", ".join(VALID_BLOOD_TYPES)
            )
        )


def get_int(prompt, minimum=None):
    """Keep asking until the user enters a valid integer."""
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a whole number.")
            continue

        if minimum is not None and value < minimum:
            print(
                "Please enter a number greater than or equal to {}.".format(
                    minimum
                )
            )
            continue

        return value


# ==============================================================================
# 3. BLOOD REQUESTS & COMPATIBILITY MODULE
# ==============================================================================

# Recipient blood type -> donor blood types they can receive
COMPATIBILITY = {
    "A+": ["A+", "A-", "O+", "O-"],
    "A-": ["A-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],  # Universal recipient
    "AB-": ["A-", "B-", "AB-", "O-"],
    "O+": ["O+", "O-"],
    "O-": ["O-"],  # O- can only receive O-
}


def find_compatible_units(patient_blood_type):
    """Returns available, non-expired, compatible units, OLDEST FIRST (FIFO)."""
    compatible = COMPATIBILITY[patient_blood_type]
    placeholders = ",".join("?" for _ in compatible)  # e.g. "?,?,?,?"
    today = date.today().isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        f"SELECT unit_id, blood_type, expiry_date FROM blood_units "
        f"WHERE status = 'available' AND expiry_date >= ? "
        f"AND blood_type IN ({placeholders}) "
        f"ORDER BY expiry_date ASC",
        [today] + compatible,
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def new_request():
    """Record a new patient request and preview matches."""
    patient_name = get_nonempty("Patient's name: ")
    patient_blood_type = get_blood_type("Patient's blood type: ")
    units_needed = get_int("Units needed: ", minimum=1)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO blood_requests "
        "(patient_name, patient_blood_type, units_needed, request_date, status) "
        "VALUES (?, ?, ?, ?, 'pending')",
        (
            patient_name,
            patient_blood_type,
            units_needed,
            date.today().isoformat(),
        ),
    )
    conn.commit()
    request_id = cur.lastrowid
    conn.close()

    print(
        "\nRequest #{} created for {} ({}).".format(
            request_id, patient_name, patient_blood_type
        )
    )

    rows = find_compatible_units(patient_blood_type)
    if len(rows) >= units_needed:
        print("Good news: {} compatible units in stock.".format(len(rows)))
    else:
        print(
            "WARNING: only {} of {} requested units available.".format(
                len(rows), units_needed
            )
        )


def check_compatibility():
    """Display allowed donor types and check available stock."""
    blood_type = get_blood_type("Patient's blood type: ")
    print(
        "\nA patient with {} can receive: {}".format(
            blood_type, ", ".join(COMPATIBILITY[blood_type])
        )
    )

    rows = find_compatible_units(blood_type)
    if not rows:
        print("No compatible units in stock.")
    else:
        print("Compatible units in stock:")
        for unit_id, unit_blood_type, expiry_date in rows:
            print(
                "  - Unit #{} ({}) - expires {}".format(
                    unit_id, unit_blood_type, expiry_date
                )
            )


def approve_or_reject_request():
    """Process pending requests by issuing blood units or rejecting."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT request_id, patient_name, patient_blood_type, units_needed, "
        "request_date FROM blood_requests WHERE status = 'pending' "
        "ORDER BY request_id"
    )
    pending = cur.fetchall()

    if not pending:
        print("\nNo pending requests.")
        conn.close()
        return

    print("\n--- Pending Requests ---")
    for (
        request_id,
        patient_name,
        patient_blood_type,
        units_needed,
        request_date,
    ) in pending:
        print(
            "#{} - {} - {} - {} unit(s) - {}".format(
                request_id,
                patient_name,
                patient_blood_type,
                units_needed,
                request_date,
            )
        )

    request_id = get_int("\nEnter the request ID to process: ", minimum=1)

    cur.execute(
        "SELECT patient_name, patient_blood_type, units_needed, status "
        "FROM blood_requests WHERE request_id = ?",
        (request_id,),
    )
    row = cur.fetchone()

    if row is None or row[3] != "pending":
        print("Request not found or not pending.")
        conn.close()
        return

    patient_name, patient_blood_type, units_needed, _ = row

    decision = get_int("1 = Approve, 2 = Reject: ", minimum=1)

    if decision == 2:
        cur.execute(
            "UPDATE blood_requests SET status = 'rejected' WHERE request_id = ?",
            (request_id,),
        )
        conn.commit()
        conn.close()
        print("Request #{} rejected.".format(request_id))
        return

    rows = find_compatible_units(patient_blood_type)
    if len(rows) < units_needed:
        print(
            "Not enough compatible stock (have {}, need {}). "
            "Request stays pending.".format(len(rows), units_needed)
        )
        conn.close()
        return

    units_to_issue = rows[:units_needed]
    issued_ids = []
    for unit_id, _, _ in units_to_issue:
        cur.execute(
            "UPDATE blood_units SET status = 'issued' WHERE unit_id = ?",
            (unit_id,),
        )
        issued_ids.append(unit_id)

    cur.execute(
        "UPDATE blood_requests SET status = 'approved' WHERE request_id = ?",
        (request_id,),
    )
    conn.commit()
    conn.close()

    print(
        "Request #{} approved. Issued unit IDs: {}".format(
            request_id, ", ".join(str(i) for i in issued_ids)
        )
    )


def view_requests():
    """List every request with its status."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT request_id, patient_name, patient_blood_type, units_needed, "
        "request_date, status FROM blood_requests ORDER BY request_id"
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("\nNo requests yet.")
        return

    print("\n{:<4} {:<15} {:<6} {:<6} {:<12} {:<10}".format(
        "ID", "Patient", "Type", "Units", "Date", "Status"
    ))
    print("-" * 60)
    for (
        request_id,
        patient_name,
        patient_blood_type,
        units_needed,
        request_date,
        status,
    ) in rows:
        print(
            "{:<4} {:<15} {:<6} {:<6} {:<12} {:<10}".format(
                request_id,
                patient_name,
                patient_blood_type,
                units_needed,
                request_date,
                status,
            )
        )


# ==============================================================================
# 4. ENTRY POINT MENU LOOP
# ==============================================================================

def print_menu():
    """Print the main menu options."""
    print("\n=== Blood Bank Management System ===")
    print("1. New blood request")
    print("2. Check blood type compatibility")
    print("3. Approve or reject a request")
    print("4. View all requests")
    print("5. Exit")


def main():
    """Run the main system loop."""
    get_connection()      # Initialize tables
    seed_sample_data()    # Seed initial test data if empty

    while True:
        print_menu()
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            new_request()
        elif choice == "2":
            check_compatibility()
        elif choice == "3":
            approve_or_reject_request()
        elif choice == "4":
            view_requests()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose a number from 1 to 5.")


if __name__ == "__main__":
    main()
    