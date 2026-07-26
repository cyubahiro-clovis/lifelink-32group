#!/usr/bin/python3
"""
donors.py - Donor management.
Contributor: Vladimir.

Handles registering donors, viewing them, searching, updating, deleting,
and finding the donors who are eligible to donate again.

Uses the team's validators: get_name() makes sure donor names contain only
letters, and get_phone() makes sure contacts are real phone numbers.
"""

import sqlite3
from datetime import date, timedelta

from database import BaseManager
from validators import (
    get_blood_type,
    get_date,
    get_int,
    get_yes_no,
    get_name,
    get_phone,
)


class DonorManager(BaseManager):
    """All donor operations. Inherits the shared database from BaseManager."""

    ELIGIBILITY_DAYS = 90  # a donor may donate again after 90 days

    def _print_table(self, rows):
        """Print a list of donor rows in a neat table."""
        print("-" * 78)
        print("{:<5}{:<24}{:<8}{:<16}{}".format(
            "ID", "Name", "Blood", "Contact", "Last Donation"))
        print("-" * 78)
        for donor_id, name, blood_type, contact, last_donation in rows:
            if last_donation is None:
                last_donation = "-"
            if contact is None:
                contact = "-"
            print("{:<5}{:<24}{:<8}{:<16}{}".format(
                donor_id, name, blood_type, contact, last_donation))
        print("-" * 78)
        print("Total: {} donor(s)".format(len(rows)))

    def register_donor(self):
        """Register a new donor in the database."""
        print("\n-- Register New Donor --")
        name = get_name("Donor name: ")
        blood_type = get_blood_type("Blood type (e.g. A+, O-): ")
        contact = get_phone("Contact (phone number): ")
        last_donation = get_date(
            "Last donation date (YYYY-MM-DD), or press Enter if none: ",
            allow_blank=True,
        )

        conn = self.connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO donors (name, blood_type, contact, last_donation_date) "
                "VALUES (?, ?, ?, ?)",
                (name, blood_type, contact, last_donation),
            )
            conn.commit()
            donor_id = cur.lastrowid
            print("Donor '{}' ({}) registered successfully with ID {}.".format(
                name, blood_type, donor_id))
        except sqlite3.Error as error:
            conn.rollback()
            print("Could not save the donor:", error)
        finally:
            conn.close()

    def view_donors(self):
        """Display all registered donors."""
        print("\n-- All Donors --")
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT donor_id, name, blood_type, contact, last_donation_date "
            "FROM donors ORDER BY donor_id"
        )
        rows = cur.fetchall()
        conn.close()

        if not rows:
            print("No donors found. Use option 1 to register the first donor.")
            return
        self._print_table(rows)

    def search_donors(self):
        """Search donors by part of their name."""
        print("\n-- Search Donors --")
        term = get_nonempty("Enter part of the donor's name: ")

        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT donor_id, name, blood_type, contact, last_donation_date "
            "FROM donors WHERE name LIKE ? ORDER BY name",
            ("%" + term + "%",),
        )
        rows = cur.fetchall()
        conn.close()

        if not rows:
            print("No donors matching '{}'.".format(term))
            return
        self._print_table(rows)

    def update_donor(self):
        """Update a donor's contact number or name."""
        print("\n-- Update Donor --")
        self.view_donors()

        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM donors")
        if cur.fetchone()[0] == 0:
            conn.close()
            return

        donor_id = get_int("Enter the ID of the donor to update: ", minimum=1)
        cur.execute(
            "SELECT name, contact FROM donors WHERE donor_id = ?", (donor_id,))
        donor = cur.fetchone()

        if donor is None:
            print("No donor with ID {}.".format(donor_id))
            conn.close()
            return

        name, contact = donor
        print("Current name: {} | Current contact: {}".format(name, contact))
        print("1. Update contact")
        print("2. Update name")
        field = input("What do you want to update? (1-2): ").strip()

        try:
            if field == "1":
                new_contact = get_phone("New contact: ")
                cur.execute(
                    "UPDATE donors SET contact = ? WHERE donor_id = ?",
                    (new_contact, donor_id),
                )
                conn.commit()
                print("Contact for {} updated successfully.".format(name))
            elif field == "2":
                new_name = get_name("New name: ")
                cur.execute(
                    "UPDATE donors SET name = ? WHERE donor_id = ?",
                    (new_name, donor_id),
                )
                conn.commit()
                print("Donor renamed to {} successfully.".format(new_name))
            else:
                print("Nothing updated - invalid option.")
        except sqlite3.Error as error:
            conn.rollback()
            print("Could not update the donor:", error)
        finally:
            conn.close()

    def delete_donor(self):
        """Delete a donor, unless blood units are still linked to them."""
        print("\n-- Delete Donor --")
        self.view_donors()

        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM donors")
        if cur.fetchone()[0] == 0:
            conn.close()
            return

        donor_id = get_int("Enter the ID of the donor to delete: ", minimum=1)
        cur.execute("SELECT name FROM donors WHERE donor_id = ?", (donor_id,))
        donor = cur.fetchone()

        if donor is None:
            print("No donor with ID {}.".format(donor_id))
            conn.close()
            return

        donor_name = donor[0]

        cur.execute(
            "SELECT COUNT(*) FROM blood_units WHERE donor_id = ?", (donor_id,))
        linked_units = cur.fetchone()[0]
        if linked_units > 0:
            print("'{}' has {} donation record(s) in the system and cannot "
                  "be deleted. This protects our donation history.".format(
                      donor_name, linked_units))
            conn.close()
            return

        if not get_yes_no("Are you sure you want to delete {}?".format(donor_name)):
            print("Deletion cancelled.")
            conn.close()
            return

        try:
            cur.execute("DELETE FROM donors WHERE donor_id = ?", (donor_id,))
            conn.commit()
            print("Donor '{}' deleted successfully.".format(donor_name))
        except sqlite3.IntegrityError:
            conn.rollback()
            print("This donor has related records and cannot be deleted.")
        except sqlite3.Error as error:
            conn.rollback()
            print("Could not delete the donor:", error)
        finally:
            conn.close()

    def find_eligible_donors(self):
        """
        List donors who can donate again: those whose last donation was more
        than 90 days ago, plus those who have never donated.
        """
        print("\n-- Donors Eligible To Donate Again --")
        cutoff = (date.today() - timedelta(days=self.ELIGIBILITY_DAYS)).isoformat()

        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT donor_id, name, blood_type, contact, last_donation_date "
            "FROM donors "
            "WHERE last_donation_date IS NULL OR last_donation_date <= ? "
            "ORDER BY donor_id",
            (cutoff,),
        )
        rows = cur.fetchall()
        conn.close()

        if not rows:
            print("No eligible donors right now.")
            return
        print("These donors can be called when stock is low:")
        self._print_table(rows)


