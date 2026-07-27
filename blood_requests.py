
#!/usr/bin/python3
"""
blood_requests.py - Patient blood requests and compatibility matching.
Owner: Achol.

This is the heart of the system. The medical compatibility rules live in one
dictionary: for each patient (recipient) blood type, the donor blood types
they can safely receive. Matching units are always offered OLDEST FIRST, so
the units closest to expiry are used before they are wasted.
"""

import sqlite3
from datetime import date

from database import BaseManager
from validators import get_name, get_blood_type, get_int, get_choice


class RequestManager(BaseManager):
    """All blood request operations."""

    # recipient blood type -> donor blood types they can receive
    COMPATIBILITY = {
        "A+":  ["A+", "A-", "O+", "O-"],
        "A-":  ["A-", "O-"],
        "B+":  ["B+", "B-", "O+", "O-"],
        "B-":  ["B-", "O-"],
        "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],  # universal recipient
        "AB-": ["A-", "B-", "AB-", "O-"],
        "O+":  ["O+", "O-"],
        "O-":  ["O-"],  # O- receives only O-, but can donate to everyone
    }

    def find_compatible_units(self, patient_blood_type):
        """Return available, non-expired, compatible units, oldest first."""
        compatible = self.COMPATIBILITY[patient_blood_type]
        placeholders = ",".join("?" for _ in compatible)
        today = date.today().isoformat()

        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT unit_id, blood_type, expiry_date FROM blood_units "
            "WHERE status = 'available' AND expiry_date >= ? "
            "AND blood_type IN ({}) "
            "ORDER BY expiry_date ASC".format(placeholders),
            [today] + compatible,
        )
        rows = cur.fetchall()
        conn.close()
        return rows

    def new_request(self):
        """Record a new patient request and immediately preview the matches."""
        print("\n-- New Blood Request --")
        patient_name = get_name("Patient's name: ")
        patient_blood_type = get_blood_type("Patient's blood type: ")
        units_needed = get_int("Units needed: ", minimum=1)

        conn = self.connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO blood_requests (patient_name, patient_blood_type, "
                "units_needed, request_date, status) VALUES (?, ?, ?, ?, 'pending')",
                (patient_name, patient_blood_type, units_needed,
                 date.today().isoformat()),
            )
            conn.commit()
            request_id = cur.lastrowid
        except sqlite3.Error as error:
            conn.rollback()
            print("Could not save the request:", error)
            return
        finally:
            conn.close()

        print("Request #{} created for {} ({}), {} unit(s) needed.".format(
            request_id, patient_name, patient_blood_type, units_needed))

        rows = self.find_compatible_units(patient_blood_type)
        if len(rows) >= units_needed:
            print("Good news: {} compatible unit(s) are in stock.".format(len(rows)))
        else:
            print("WARNING: only {} of the {} unit(s) requested are available.".format(
                len(rows), units_needed))
            print("Tip: use Donor Management > Find eligible donors to call donors.")

    def check_compatibility(self):
        """Explain who a patient can receive from, and show matching stock."""
        print("\n-- Blood Compatibility Check --")
        blood_type = get_blood_type("Patient's blood type: ")
        print("A patient with {} can safely receive: {}".format(
            blood_type, ", ".join(self.COMPATIBILITY[blood_type])))

        rows = self.find_compatible_units(blood_type)
        if not rows:
            print("No compatible units are currently in stock.")
            return

        print("Compatible units in stock (oldest first, use these first):")
        for unit_id, unit_blood_type, expiry_date in rows:
            print("  Unit #{} ({}) - expires {}".format(
                unit_id, unit_blood_type, expiry_date))

    def view_requests(self):
        """List every request with its status."""
        print("\n-- All Blood Requests --")
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT request_id, patient_name, patient_blood_type, units_needed, "
            "request_date, status FROM blood_requests ORDER BY request_id"
        )
        rows = cur.fetchall()
        conn.close()

        if not rows:
            print("No requests have been made yet.")
            return

        print("-" * 74)
        print("{:<5}{:<20}{:<8}{:<8}{:<14}{}".format(
            "ID", "Patient", "Type", "Units", "Date", "Status"))
        print("-" * 74)
        for row in rows:
            print("{:<5}{:<20}{:<8}{:<8}{:<14}{}".format(*row))
        print("-" * 74)

    def approve_or_reject_request(self):
        """
        Process a pending request. Approving issues the oldest compatible
        units, updates the stock, and writes the distribution record.
        """
        print("\n-- Approve Or Reject A Request --")
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT request_id, patient_name, patient_blood_type, units_needed, "
            "request_date FROM blood_requests WHERE status = 'pending' "
            "ORDER BY request_id"
        )
        pending = cur.fetchall()

        if not pending:
            print("There are no pending requests.")
            conn.close()
            return

        print("Pending requests:")
        for request_id, patient, blood_type, units, request_date in pending:
            print("  #{} - {} - {} - {} unit(s) - {}".format(
                request_id, patient, blood_type, units, request_date))

        request_id = get_int("Enter the request ID to process: ", minimum=1)
        cur.execute(
            "SELECT patient_name, patient_blood_type, units_needed, status "
            "FROM blood_requests WHERE request_id = ?",
            (request_id,),
        )
        row = cur.fetchone()

        if row is None:
            print("There is no request with ID {}.".format(request_id))
            conn.close()
            return
        if row[3] != "pending":
            print("Request #{} has already been {}.".format(request_id, row[3]))
            conn.close()
            return

        patient_name, patient_blood_type, units_needed, _ = row
        decision = get_choice("1 = Approve, 2 = Reject: ", ["1", "2"])

        try:
            if decision == "2":
                cur.execute(
                    "UPDATE blood_requests SET status = 'rejected' "
                    "WHERE request_id = ?", (request_id,))
                conn.commit()
                print("Request #{} for {} has been rejected.".format(
                    request_id, patient_name))
                return

            units = self.find_compatible_units(patient_blood_type)
            if len(units) < units_needed:
                print("Not enough compatible stock (have {}, need {}). "
                      "Request #{} stays pending.".format(
                          len(units), units_needed, request_id))
                return

            issued_ids = []
            today = date.today().isoformat()
            for unit_id, _, _ in units[:units_needed]:
                cur.execute(
                    "UPDATE blood_units SET status = 'issued' WHERE unit_id = ?",
                    (unit_id,),
                )
                cur.execute(
                    "INSERT INTO issued_units (request_id, unit_id, issue_date) "
                    "VALUES (?, ?, ?)",
                    (request_id, unit_id, today),
                )
                issued_ids.append(unit_id)

            cur.execute(
                "UPDATE blood_requests SET status = 'approved' "
                "WHERE request_id = ?", (request_id,))
            conn.commit()

            print("Request #{} approved for {}.".format(request_id, patient_name))
            print("Issued unit(s): {} - the stock has been updated and the "
                  "distribution recorded.".format(
                      ", ".join("#" + str(i) for i in issued_ids)))
        except sqlite3.Error as error:
            conn.rollback()
            print("Could not process the request:", error)
        finally:
            conn.close()
