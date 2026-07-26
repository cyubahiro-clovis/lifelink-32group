# LifeLink: Blood Bank Inventory and Donor Management System

A menu driven, command-line application built with python and MySQL by Group32, ALU BSE Year one, Trimester 2(PLP 2).

## The problem 
Rwanda is known worldwide for its blood *delivery* network, where drones carry blood from national centres to hospitals. But delivery is only one part of the chain. Inside an individual hospital or health facility, the local blood bank still has to manage its own records: which units are on the shelf, which expire this week, which donors can be called, and which patient needs which blood type.

## features

Register, view and delete donors, and find donors eligible to donate again (last donation more than 90 days ago)
-Record donations: each unit gets an automatically calculated expiry date (42-day shelf life, using python's datetime)
-View stock by blood type
-Flag units expiring within 7 days and remove expired units
-Create patient blood requests with automatic compatibility rules are stored as a python dictionary), issuing the oldest compatible units first to reduce waste
-Approve or reject requests, with stock updated automatically 
-Reports: inventory report, donation history, request log 

## How to run

Requirements: Python3

'''
git clone <paste repo-url-here>
cd <repo-folder>
python seed_data.py   #optional: load sample data for testing
python main.py
'''
## Project Structure

main.py: Entry point for main menu and sub menu (Clovis)
database.py: MySQL coonection and table creation (Clovis)
donors.py: Donor management functions (Vladimir)
inventory.py: Blood units, stock and expiry (Christian)
blood_requests.py: Requests and compatibility matching (Achol) 
reports.py: Report (Nziza)
validators.py: Input validation helpers (no crashes!!) (Nissi)
seed_data.py: Sample/demo data (Nziza)

## Database schema

-**donors**(donor_id, name, blood_type, contact, last_donation_date)
-**blood_units**(unit_id, blood_typ, collection_date, expiry_date, status, donor_id to donors)
-**blood_requests**(request_id, patient_name, patience_blood_type, units_needed, request_date, status)

## Data privacy

This is a student prototype: it uses **made up test data only**, stored in a local MySQL file on the team's machines. Input validation prevents invalid blood types, dates and numbers from entering the database.

## Team- Group32

Cyubahiro clovis, Nziza Ephrem, Vladimir, Achol, Nissi, Christian Muragwa.
