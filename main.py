#!/usr/bin/python3
"""
LifeLink:This a Blood Bank Inventory and Donor Management System
Group 32: ALU BSE Year 1, Trimester 2, Peer Learning Project 2

This is the only file you run:   python3 main.py

The LifeLinkApp class below builds one Database object and hands it to every
manager, so the whole application shares one database connection setting.
"""

import sqlite3
import sys

from database import Database
from donors import DonorManager
from inventory import InventoryManager
from blood_requests import RequestManager
from reports import ReportManager
from alerts import AlertEngine
from validators import get_choice, pause


class LifeLinkApp:
    """The command-line application: login, menus, and the main loop."""

    MAX_LOGIN_ATTEMPTS = 3

    def __init__(self):
        self.db = Database()
        self.db.create_tables()
        self.donors = DonorManager(self.db)
        self.inventory = InventoryManager(self.db)
        self.requests = RequestManager(self.db)
        self.reports = ReportManager(self.db)
        self.alerts = AlertEngine(self.db)
        self.user = None

<<<<<<< Updated upstream
    # Login
=======
def reports_menu():
    while True:
        print("\n--- REPORTS ---")
        print("1. Inventory report")
        print("2. Donation history")
        print("3. Requeest log")
        print("4. Back to main menu")
        choice = input("Enter your choice (1-4): ").strip()
        if choice == "1":
            reports.inventory_report()
        elif choice == "2":
            reports.donations_history()
        elif choice == "3":
            reports.request_log()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 4.")
>>>>>>> Stashed changes

    def login(self):
        """Ask for staff credentials. Returns True when the login succeeds."""
        print("\n-- STAFF LOGIN --")
        print("Only authorised blood bank staff may open patient "
              "and donor records.")

        for attempt in range(self.MAX_LOGIN_ATTEMPTS, 0, -1):
            username = input("Username: ").strip()
            password = input("Password: ").strip()

            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT username FROM staff WHERE username = ? AND password = ?",
                (username, password),
            )
            row = cur.fetchone()
            conn.close()

            if row:
                self.user = row[0]
                print("\nWelcome, {}!".format(self.user))
                return True

            if attempt > 1:
                print("Wrong username or password. {} attempt(s) left.".format(
                    attempt - 1))

        print("Access denied. Closing the system.")
        return False

    # Sub-menus
  
    def donor_menu(self):
        while True:
            print("\n--- DONOR MANAGEMENT ---")
            print("1. Register new donor")
            print("2. View all donors")
            print("3. Search donors by name")
            print("4. Update donor details")
            print("5. Delete donor")
            print("6. Find eligible donors (last donation over 90 days ago)")
            print("7. Back to main menu")
            choice = get_choice("Enter your choice (1-7): ",
                                ["1", "2", "3", "4", "5", "6", "7"])

            if choice == "7":
                break
            actions = {
                "1": self.donors.register_donor,
                "2": self.donors.view_donors,
                "3": self.donors.search_donors,
                "4": self.donors.update_donor,
                "5": self.donors.delete_donor,
                "6": self.donors.find_eligible_donors,
            }
            actions[choice]()
            pause()

    def inventory_menu(self):
        while True:
            print("\n--- BLOOD INVENTORY ---")
            print("1. Add blood unit (record a donation)")
            print("2. View stock by blood type")
            print("3. Check blood expiry dates (expiring within 7 days)")
            print("4. Remove expired units")
            print("5. Low stock alert")
            print("6. Back to main menu")
            choice = get_choice("Enter your choice (1-6): ",
                                ["1", "2", "3", "4", "5", "6"])

            if choice == "6":
                break
            actions = {
                "1": self.inventory.add_blood_unit,
                "2": self.inventory.view_stock,
                "3": self.inventory.check_expiring_units,
                "4": self.inventory.remove_expired_units,
                "5": self.alerts.low_stock_alert,
            }
            actions[choice]()
            pause()

    def requests_menu(self):
        while True:
            print("\n--- BLOOD REQUESTS ---")
            print("1. New blood request")
            print("2. Check blood compatibility")
            print("3. Approve or reject a request")
            print("4. View all requests")
            print("5. Back to main menu")
            choice = get_choice("Enter your choice (1-5): ",
                                ["1", "2", "3", "4", "5"])

            if choice == "5":
                break
            actions = {
                "1": self.requests.new_request,
                "2": self.requests.check_compatibility,
                "3": self.requests.approve_or_reject_request,
                "4": self.requests.view_requests,
            }
            actions[choice]()
            pause()

    def reports_menu(self):
        while True:
            print("\n--- REPORTS ---")
            print("1. Inventory report")
            print("2. Donation history")
            print("3. Request log")
            print("4. Distribution log (who received which unit)")
            print("5. Back to main menu")
            choice = get_choice("Enter your choice (1-5): ",
                                ["1", "2", "3", "4", "5"])

            if choice == "5":
                break
            actions = {
                "1": self.reports.inventory_report,
                "2": self.reports.donation_history,
                "3": self.reports.request_log,
                "4": self.reports.distribution_log,
            }
            actions[choice]()
            pause()

    # Main loop

    def run(self):
        print("=" * 52)
        print("          LIFELINK BLOOD BANK SYSTEM")
        print("      Group 32 - ALU BSE Year 1 Trimester 2")
        print("=" * 52)

        if not self.login():
            return

        self.alerts.startup_summary()

        while True:
            print("\n========== MAIN MENU ==========")
            print("1. Donor Management")
            print("2. Blood Inventory")
            print("3. Blood Requests")
            print("4. Reports")
            print("5. Exit")
            choice = get_choice("Enter your choice (1-5): ",
                                ["1", "2", "3", "4", "5"])

            if choice == "1":
                self.donor_menu()
            elif choice == "2":
                self.inventory_menu()
            elif choice == "3":
                self.requests_menu()
            elif choice == "4":
                self.reports_menu()
            elif choice == "5":
                print("\nThank you for using LifeLink. Goodbye!")
                break


def main():
    """Start the application and never show the user a Python traceback."""
    try:
        LifeLinkApp().run()
    except (KeyboardInterrupt, EOFError):
        print("\n\nSystem closed. Goodbye!")
    except sqlite3.Error as error:
        print("\nA database error occurred:", error)
        print("Try deleting lifelink.db and running: python3 seed_data.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
