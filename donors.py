#!/usr/bin/python3
"""
donors.py - Donor management.
Contributor: Vladimir.

This module handles donor registration, viewing donors,
deleting donors, and finding eligible donors.
"""

import sqlite3
from datetime import date, timedelta

import database
from validators import (
    get_blood_type,
    get_date,
    get_int,
    get_yes_no,
    get_name,
    get_phone,
)


def register_donor():
    """Register a new donor in the database."""
    print("\n-- Register New Donor --")

    name = get_name("Donor name: ")
    blood_type = get_blood_type("Blood type (e.g. A+, O-): ")
    contact = get_phone("Contact (phone number): ")
    last_donation = get_date(
        "Last donation date (YYYY-MM-DD), or press Enter if none: ",
        allow_blank=True,
    )

    conn = database.get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO donors "
        "(name, blood_type, contact, last_donation_date) "
        "VALUES (?, ?, ?, ?)",
        (name, blood_type, contact, last_donation),
    )

    conn.commit()
    donor_id = cur.lastrowid
    conn.close()

    print(
        f"Donor '{name}' ({blood_type}) registered successfully "
        f"with ID {donor_id}."
    )


def view_donors():
    """Display all registered donors."""
    print("\n-- View Donors --")

    conn = database.get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT donor_id, name, blood_type, contact, last_donation_date
        FROM donors
        ORDER BY donor_id
        """
    )

    donors = cur.fetchall()

    if not donors:
        print("No donors found.")
        conn.close()
        return

    print("-" * 75)
    print(
        f"{'ID':<4} "
        f"{'Name':<22} "
        f"{'Blood':<7} "
        f"{'Contact':<16} "
        f"{'Last Donation'}"
    )
    print("-" * 75)

    for donor in donors:
        donor_id, name, blood_type, contact, last_donation = donor

        if last_donation is None:
            last_donation = "-"

        print(
            f"{donor_id:<4} "
            f"{name:<22} "
            f"{blood_type:<7} "
            f"{contact:<16} "
            f"{last_donation}"
        )

    print("-" * 75)
    conn.close()


def delete_donor():
    """Delete a donor who has no related donation records."""
    print("\n-- Delete Donor --")

    view_donors()

    donor_id = get_int(
        "Enter the ID of the donor to delete: ",
        minimum=1,
    )

    conn = database.get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT name FROM donors WHERE donor_id = ?",
        (donor_id,),
    )

    donor = cur.fetchone()

    if donor is None:
        print(f"No donor with ID {donor_id}.")
        conn.close()
        return

    donor_name = donor[0]

    confirmed = get_yes_no(
        f"Are you sure you want to delete {donor_name}?"
    )

    if not confirmed:
        print("Deletion cancelled.")
        conn.close()
        return

    try:
        cur.execute(
            "DELETE FROM donors WHERE donor_id = ?",
            (donor_id,),
        )

        conn.commit()
        print(f"Donor '{donor_name}' deleted successfully.")

    except sqlite3.IntegrityError:
        conn.rollback()
        print(
            "This donor has donation records and cannot be deleted."
        )

    finally:
        conn.close()


def find_eligible_donors():
    """Display donors eligible to donate again."""
    print("\n-- Eligible Donors --")

    cutoff = (date.today() - timedelta(days=90)).isoformat()

    conn = database.get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT donor_id, name, blood_type, contact, last_donation_date
        FROM donors
        WHERE last_donation_date IS NULL
        OR last_donation_date <= ?
        ORDER BY donor_id
        """,
        (cutoff,),
    )

    donors = cur.fetchall()

    if not donors:
        print("No eligible donors right now.")
        conn.close()
        return

    print("-" * 75)
    print(
        f"{'ID':<4} "
        f"{'Name':<22} "
        f"{'Blood':<7} "
        f"{'Contact':<16} "
        f"{'Last Donation'}"
    )
    print("-" * 75)

    for donor in donors:
        donor_id, name, blood_type, contact, last_donation = donor

        if last_donation is None:
            last_donation = "-"

        print(
            f"{donor_id:<4} "
            f"{name:<22} "
            f"{blood_type:<7} "
            f"{contact:<16} "
            f"{last_donation}"
        )

    print("-" * 75)
    conn.close()
