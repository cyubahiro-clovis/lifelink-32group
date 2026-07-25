#!/usr/bin/python3
"""Reporting functions for the LifeLink Blood Bank system.

"""
from db import get_connection


def inventory_report():
    """Print current blood stock grouped by type and status."""
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT blood_type, status, COUNT(*) AS units, "
        "SUM(quantity_ml) AS total_ml "
        "FROM blood_units "
        "GROUP BY blood_type, status "
        "ORDER BY blood_type, status"
    ).fetchall()
    conn.close()

    print("\n===== INVENTORY REPORT =====")
    if not rows:
        print("No blood units in stock.")
        return
    print("{:<6}{:<12}{:<8}{:<12}".format(
        "Type", "Status", "Units", "Total (ml)"))
    print("-" * 38)
    for r in rows:
        print("{:<6}{:<12}{:<8}{:<12}".format(
            r["blood_type"], r["status"], r["units"], r["total_ml"]))


def donation_history(donor_id=None):
    """Print donation records, optionally filtered to one donor."""
    conn = get_connection()
    cur = conn.cursor()
    query = (
        "SELECT d.donation_id, dn.full_name, dn.blood_type, "
        "d.donation_date "
        "FROM donations d "
        "JOIN donors dn ON d.donor_id = dn.donor_id"
    )
    params = ()
    if donor_id is not None:
        query += " WHERE dn.donor_id = ?"
        params = (donor_id,)
    query += " ORDER BY d.donation_date DESC"
    rows = cur.execute(query, params).fetchall()
    conn.close()

    print("\n===== DONATION HISTORY =====")
    if not rows:
        print("No donations recorded.")
        return
    print("{:<5}{:<26}{:<6}{:<12}".format("ID", "Donor", "Type", "Date"))
    print("-" * 43)
    for r in rows:
        print("{:<5}{:<26}{:<6}{:<12}".format(
            r["donation_id"], r["full_name"],
            r["blood_type"], r["donation_date"]))


def request_log(status=None):
    """Print hospital blood requests, optionally filtered by status."""
    conn = get_connection()
    cur = conn.cursor()
    query = (
        "SELECT request_id, requester_name, hospital, blood_type, "
        "quantity_ml, status, request_date FROM requests"
    )
    params = ()
    if status is not None:
        query += " WHERE status = ?"
        params = (status,)
    query += " ORDER BY request_date DESC"
    rows = cur.execute(query, params).fetchall()
    conn.close()

    print("\n===== REQUEST LOG =====")
    if not rows:
        print("No requests found.")
        return
    print("{:<5}{:<15}{:<26}{:<6}{:<6}{:<10}{:<12}".format(
        "ID", "Requester", "Hospital", "Type",
        "ml", "Status", "Date"))
    print("-" * 74)
    for r in rows:
        print("{:<5}{:<15}{:<26}{:<6}{:<6}{:<10}{:<12}".format(
            r["request_id"], r["requester_name"], r["hospital"],
            r["blood_type"], r["quantity_ml"], r["status"],
            r["request_date"]))


def _menu():
    """Standalone menu for testing reports.py on its own."""
    options = {
        "1": inventory_report,
        "2": donation_history,
        "3": request_log,
    }
    while True:
        print("\n--- Reports Menu ---")
        print("1. Inventory Report")
        print("2. Donation History")
        print("3. Request Log")
        print("0. Back")
        choice = input("Choose an option: ").strip()
        if choice == "0":
            break
        action = options.get(choice)
        if action:
            action()
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    _menu()
