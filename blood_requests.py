#!/usr/bin/python3
"""
blood_requests.py - Patient blood requests and compatibility matching.
Owner: Achol.

This is the star module of the demo. The medical rule is captured in ONE
dictionary: for each patient (recipient) blood type, the list of donor blood
types they can safely receive. This is exactly what we promised in PLP-1.
"""

from datetime import date

import db
from validators import get_nonempty, get_blood_type, get_int

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
    conn = db.get_connection()
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

    conn = db.get_connection()
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
    conn = db.get_connection()
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

    decision = get_int("1 = Approve, 2 = Reject: ", minimum=1, maximum=2)

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
    conn = db.get_connection()
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