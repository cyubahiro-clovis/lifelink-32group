#!/usr/bin/python3
""""
LifeLink is a Blood Bank Inventory and Donor Management System
Group 32: ALU BSE, Year 1, Trimester 2, Peer Learning Project 2

Entry point. Run with: python main.py
"""

import database
import donors
import inventory
import blood_requests
import reports

def donor_menu():
    while True:
        print("\n---Donor MANAGEMENT ---")
        print("1. Register new donor")
        print("2. View donor info")
        print("3. Delete donor details")
        print("4. Find eligible donors (last donation over 90 days)")
        print("5. Back to main menu")
        choice = input("Enter your choice (1-5): ").strip()
        if choice == "1":
            donors.register_donor()
        elif choice == "2":
            donors.view_donors()
        elif choice == "3":
            donors.delete_donor()
        elif choice == "4":
            donors.find_eligible_donors()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")


def inventory_menu():
    while True:
        print("\n--- BLOOD INVENTORY ---")
        print("1. Add blood units (record a donation)")
        print("2. View stock by blood type")
        print("3. Check blood expiry dates (expiring within 7 days)")
        print("4. Remove expired units")
        print("5. Back to main menu")
        choice = input("Enter your choice (1-5): ").strip()
        if choice == "1":
            inventory.add_blood_unit()
        elif choice == "2":
            inventory.view_stock()
        elif choice == "3":
            inventory.check_expiring_units()
        elif choice == "4":
            inventory.remove_expired_units()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5")

def requests_menu():
    while True:
        print("\n --- BLOOD REQUESTS ---")
        print("1. New blood request")
        print("2. Check blood compatibility for a blood type")
        print("3. Approve or reject a request")
        print("4. View all requests")
        print("5. Back to main menu")
        choice = input("Enter your choice (1-5): ").strip()
        if choice == "1":
            blood_requests.new_request()
        elif choice == "2":
            blood_requests.check_compatibility()
        elif choice == "3":
            blood_requests.approve_or_reject_request()
        elif choice == "4":
            blood_requests.view_requests()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")


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
            report.donations_history()
        elif choice == "3":
            reports.request_log()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 4.")



def main():
    database.create_tables()
    print("=" * 38)
    print("     LIFELINK BLOOD BANK SYSTEM")
    print("   Group 32 - ALU BSE Year 1 Trimester 2")
    print("=" * 38)
    while True:
        print("\n========== MAIN MENU ==========")
        print("1. Donor Management")
        print("2. Blood Inventory")
        print("3. Blood Requests")
        print("4. Reports")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ").strip()
        if choice == "1":
            donor_menu()
        elif choice == "2":
            inventory_menu()
        elif choice == "3":
            requests_menu()
        elif choice == "4":
            reports_menu()
        elif choice == "5":
            print("Thank you for using Lifelink!")
            break
        else:
            print("invalid choice. Please enter a number from 1 to 5.")


if__name__ == "__main__":
    main()
