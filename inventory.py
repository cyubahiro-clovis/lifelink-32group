#!/usr/bin/python3
"""
inventory.py - Blood units, stock levels and expiry.

The key rule of this module: expiry_date = collection_date + 42 days
(the shelf life we assumed in our PLP-1 document), calculated automatically
with Python's datetime module so staff never work it out by hand.
"""

import sqlite3
from datetime import date, timedelta

from database import BaseManager
from validators import get_blood_type, get_date, get_int, get_yes_no


class InventoryManager(BaseManager):
    """All blood unit operations."""

    SHELF_LIFE_DAYS = 42
    EXPIRY_WARNING_DAYS = 7
    DEFAULT_VOLUME_ML = 450

    def add_blood_unit(self):
        """Record a donated blood unit and calculate its expiry date."""
        print("\n-- Add Blood Unit --")
        blood_type = get_blood_type("Blood type: ")

        collection = get_date(
            "Collection date (YYYY-MM-DD), or press Enter for today: ",
            allow_blank=True,
        )
        if collection is None:
            collection = date.today().isoformat()

        collection_obj = date.fromisoformat(collection)
        if collection_obj > date.today():
            print("A collection date in the future is not allowed. "
                  "Using today's date instead.")
            collection_obj = date.today()
            collection = collection_obj.isoformat()

        expiry = (collection_obj + timedelta(days=self.SHELF_LIFE_DAYS)).isoformat()

        donor_id = None
        conn = self.connect()
        try:
            cur = conn.cursor()

            if get_yes_no("Link this unit to a registered donor?"):
                donor_id = get_int("Donor ID: ", minimum=1)
                cur.execute(
                    "SELECT name FROM donors WHERE donor_id = ?", (donor_id,))
                donor = cur.fetchone()
                if donor is None:
                    print("Donor not found. The unit will be saved without "
                          "a donor link.")
                    donor_id = None
                else:
                    # Recording a donation also updates the donor's last date.
                    cur.execute(
                        "UPDATE donors SET last_donation_date = ? "
                        "WHERE donor_id = ?",
                        (collection, donor_id),
                    )
                    print("Donation linked to {}.".format(donor[0]))

            cur.execute(
                "INSERT INTO blood_units "
                "(blood_type, quantity_ml, collection_date, expiry_date, "
                "status, donor_id) VALUES (?, ?, ?, ?, 'available', ?)",
                (blood_type, self.DEFAULT_VOLUME_ML, collection, expiry, donor_id),
            )
            unit_id = cur.lastrowid
            conn.commit()

            days_left = (date.fromisoformat(expiry) - date.today()).days
            print("Unit #{} ({}) added. Expires on {} ({} days left).".format(
                unit_id, blood_type, expiry, days_left))
        except sqlite3.Error as error:
            conn.rollback()
            print("Could not save the blood unit:", error)
        finally:
            conn.close()

    def view_stock(self):
        """Show how many usable units are available for each blood type."""
        print("\n-- Current Stock By Blood Type --")
        today = date.today().isoformat()

        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT blood_type, COUNT(*), SUM(quantity_ml) FROM blood_units "
            "WHERE status = 'available' AND expiry_date >= ? "
            "GROUP BY blood_type ORDER BY blood_type",
            (today,),
        )
        rows = cur.fetchall()
        conn.close()

        if not rows:
            print("No blood units in stock.")
            return

        print("-" * 44)
        print("{:<12}{:<10}{}".format("Blood Type", "Units", "Volume (ml)"))
        print("-" * 44)
        total_units = 0
        for blood_type, count, volume in rows:
            total_units += count
            print("{:<12}{:<10}{}".format(blood_type, count, volume))
        print("-" * 44)
        print("Total usable units in stock: {}".format(total_units))

    def check_expiring_units(self):
        """Flag the units that will expire within the next 7 days."""
        print("\n-- Units Expiring Soon --")
        today = date.today()
        limit = today + timedelta(days=self.EXPIRY_WARNING_DAYS)

        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT unit_id, blood_type, expiry_date FROM blood_units "
            "WHERE status = 'available' AND expiry_date >= ? "
            "AND expiry_date <= ? ORDER BY expiry_date",
            (today.isoformat(), limit.isoformat()),
        )
        rows = cur.fetchall()
        conn.close()

        if not rows:
            print("No units are expiring within the next {} days.".format(
                self.EXPIRY_WARNING_DAYS))
            return

        print("WARNING: use these units first, before they are wasted!")
        for unit_id, blood_type, expiry in rows:
            days_left = (date.fromisoformat(expiry) - today).days
            print("  Unit #{} ({}) expires on {} - {} day(s) left".format(
                unit_id, blood_type, expiry, days_left))

    def remove_expired_units(self):
        """Mark units that are already past their expiry date."""
        print("\n-- Remove Expired Units --")
        today = date.today().isoformat()

        conn = self.connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE blood_units SET status = 'expired' "
                "WHERE status = 'available' AND expiry_date < ?",
                (today,),
            )
            count = cur.rowcount
            conn.commit()
            if count:
                print("{} expired unit(s) removed from usable stock.".format(count))
                print("They stay in the database for the inventory report, "
                      "marked as 'expired'.")
            else:
                print("No expired units found - the stock is clean.")
        except sqlite3.Error as error:
            conn.rollback()
            print("Could not update the stock:", error)
        finally:
            conn.close()

