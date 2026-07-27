# LifeLink — Blood Bank Inventory and Donor Management System

A menu-driven, command-line application built with **Python 3 and SQLite** by **Group 32**, African Leadership University, BSE Year 1 Trimester 2 (Peer Learning Project 2).


## The problem we are solving

Rwanda is known worldwide for its blood *delivery* network, where drones carry blood from national centres to hospitals. But delivery is only one part of the chain. Inside an individual hospital or health facility, the local blood bank still has to manage its own records: which units are on the shelf, which expire this week, which donors can be called, and which patient needs which blood type.

In many facilities this is still done on paper. The result is:

- **Wastage**: units expire unnoticed in storage.
- **Slow emergencies**: staff search paper registers by hand to find compatible blood, while every minute counts.
- **Weak reporting**: no reliable picture of stock for planning donation campaigns.

**LifeLink digitises this facility-level record keeping.**


## Quick start

Requirements: **Python 3.6 or newer**. Nothing to install — we only use the standard library (`sqlite3`, `datetime`, `os`, `sys`).

```
git clone https://github.com/cyubahiro-clovis/lifelink-32group.git
cd lifelink-32group
python3 seed_data.py
python3 main.py
```

**Logins for the demo (two roles):**

| Username | Password | Role | Can do |
|---|---|---|---|
| `admin` | `blood2026` | administrator | everything, including approving requests, deleting donors and removing expired units |
| `tech` | `blood2026` | technician | registers donors, records donations, creates requests, reads all reports but cannot approve requests or delete records |

The database file `lifelink.db` is created automatically on first run. To start from a clean database, delete `lifelink.db` and run `python3 seed_data.py` again.


## Features

**Staff accounts and roles**
- Login required before any record can be opened, with three attempts
- Two roles stored in the `staff` table: administrator and technician
- Administrator-only actions are marked `[admin only]` in the menus and refused politely for a technician
- Log out and switch user without restarting the application

**Donor management**
- Register a donor (name, blood type, contact, last donation date)
- View all donors, search donors by name, update contact or name
- Delete a donor — blocked automatically if donation records exist, protecting our history
- Find eligible donors: those who last donated more than 90 days ago, or never

**Blood inventory**
- Add a blood unit; the expiry date is calculated automatically as collection date + 42 days
- View stock by blood type, with unit counts and total volume
- Check units expiring within 7 days, showing days remaining
- Remove expired units from usable stock (they stay in the database for reporting)

**Blood requests and compatibility matching**
- Create a patient request
- Check compatibility: the medical rules are stored in one Python dictionary, so the system knows an A+ patient can also receive A−, O+ and O−
- Approve or reject a request. Approving issues the **oldest compatible units first** (FIFO), so blood is used before it expires, updates the stock, and records the distribution
- Insufficient stock never crashes the system: the request stays pending with a clear warning

**Alert engine**
- A dashboard on startup: units in stock, units expiring soon, pending requests
- Low stock alerts per blood type, with a threshold of 3 units

**Reports**
- Inventory report with a wastage rate
- Donation history (joins blood units to donors)
- Request log
- Distribution log — which unit went to which patient, and when (joins three tables)


## How the code is organised (object-oriented design)

The application uses classes. `Database` owns the SQLite file and the schema. `BaseManager` is the parent class that holds that database object, and every feature manager **inherits** from it, so the whole application shares one database configuration


LifeLinkApp  (main.py)
   ├── Database: This owns lifelink.db and the schema
   ├── DonorManager(BaseManager): donors.py
   ├── InventoryManager(BaseManager): inventory.py
   ├── RequestManager(BaseManager): blood_requests.py
   ├── ReportManager(BaseManager): reports.py
   └── AlertEngine(BaseManager): alerts.py`

| File | Purpose | Owner |
|---|---|---|
| `main.py` | Entry point: `LifeLinkApp` class, login, menus | Clovis |
| `database.py` | `Database` and `BaseManager` classes, schema | Clovis |
| `donors.py` | `DonorManager` — donor operations | Vladimir |
| `inventory.py` | `InventoryManager` — units, stock, expiry | Christian |
| `blood_requests.py` | `RequestManager` — requests, compatibility | Achol |
| `reports.py` | `ReportManager` — the four reports | Nziza |
| `alerts.py` | `AlertEngine` — low stock and startup dashboard | Nissi |
| `validators.py` | Input validation helpers used by every module | Nissi |
| `seed_data.py` | Sample data for testing and the demo | Nziza |


## Database schema

| Table | Columns |
|---|---|
| `donors` | donor_id, name, blood_type, contact, last_donation_date |
| `blood_units` | unit_id, blood_type, quantity_ml, collection_date, expiry_date, status, donor_id → donors |
| `blood_requests` | request_id, patient_name, patient_blood_type, units_needed, request_date, status |
| `issued_units` | issue_id, request_id → blood_requests, unit_id → blood_units, issue_date |
| `staff` | staff_id, username, password, role |

Foreign keys are enabled with `PRAGMA foreign_keys = ON`. A blood unit records both the stock item and the donation that produced it, through `donor_id` and `collection_date`. `issued_units` is the distribution record: it links a request to the exact units issued for it.


## Error validation

Every user input passes through `validators.py`, which loops until the input is valid instead of crashing:

- Letters typed where a number is expected
- Blood types outside the 8 valid groups (lowercase `a+` is accepted and corrected to `A+`)
- Dates that are not in `YYYY-MM-DD` format, and collection dates in the future
- Empty fields
- Donor names that contain digits, and phone numbers that are not real numbers
- Menu choices outside the range
- Database errors are caught with `try / except sqlite3.Error` and rolled back
- Empty tables print a friendly message, never a crash
- Pressing Ctrl+C closes the system cleanly instead of showing a Python traceback


## Data privacy

This is a student prototype. It uses **invented test data only** — no real patient or donor information. The database is a local file on the team's machines, and a staff login protects access to the records. Input validation keeps invalid data out of the database.

Access is controlled by role: a technician cannot approve a blood release or delete records. Known limitation, stated openly: passwords are stored as plain text. A real deployment would hash them, add per-user roles and an audit trail, and comply with health-data protection rules.


## Team: Group 32

Cyubahiro Clovis, Nziza Ephrem, Vladimir, Achol, Nissi, Christian Muragwa.
