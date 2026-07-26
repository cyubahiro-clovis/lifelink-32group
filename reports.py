#!/usr/bin/python3
"""
reports.py - Reports for decision making.
Owner: Nziza.

Reports are SELECT queries printed as neat tables. They answer the questions
a blood bank administrator actually asks: what do we have, where did it come
from, who asked for blood, and who received it.
"""

from database import BaseManager


class ReportManager(BaseManager):
    """All reporting operations."""

    def inventory_report(self):
        """Full picture of the blood bank: every unit grouped by type and status."""
        print("\n===== INVENTORY REPORT =====")
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT blood_type, status, COUNT(*), SUM(quantity_ml) "
            "FROM blood_units GROUP BY blood_type, status "
            "ORDER BY blood_type, status"
        )
        rows = cur.fetchall()

        if not rows:
            print("No blood units have been recorded yet.")
            conn.close()
            return

        print("-" * 50)
        print("{:<12}{:<12}{:<10}{}".format(
            "Blood Type", "Status", "Units", "Volume (ml)"))
        print("-" * 50)
        for blood_type, status, units, volume in rows:
            print("{:<12}{:<12}{:<10}{}".format(blood_type, status, units, volume))
        print("-" * 50)

        cur.execute("SELECT COUNT(*) FROM blood_units")
        total = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM blood_units WHERE status = 'available'")
        available = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM blood_units WHERE status = 'issued'")
        issued = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM blood_units WHERE status = 'expired'")
        expired = cur.fetchone()[0]
        conn.close()

        print("Total units: {} | Available: {} | Issued: {} | Expired: {}".format(
            total, available, issued, expired))
        if total:
            waste_rate = round((expired / total) * 100, 1)
            print("Wastage rate: {}% (the number our system exists to reduce)".format(
                waste_rate))

    def donation_history(self):
        """Every donation, with the donor's name (a JOIN across two tables)."""
        print("\n===== DONATION HISTORY =====")
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT u.unit_id, u.blood_type, u.collection_date, u.status, "
            "COALESCE(d.name, 'Anonymous') "
            "FROM blood_units u "
            "LEFT JOIN donors d ON u.donor_id = d.donor_id "
            "ORDER BY u.collection_date DESC, u.unit_id DESC"
        )
        rows = cur.fetchall()
        conn.close()

        if not rows:
            print("No donations have been recorded yet.")
            return

        print("-" * 66)
        print("{:<8}{:<8}{:<14}{:<12}{}".format(
            "Unit", "Type", "Collected", "Status", "Donor"))
        print("-" * 66)
        for unit_id, blood_type, collected, status, donor in rows:
            print("{:<8}{:<8}{:<14}{:<12}{}".format(
                "#" + str(unit_id), blood_type, collected, status, donor))
        print("-" * 66)
        print("Total: {} donation(s) recorded".format(len(rows)))

    def request_log(self):
        """Every request ever made and what happened to it."""
        print("\n===== REQUEST LOG =====")
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT request_id, patient_name, patient_blood_type, units_needed, "
            "request_date, status FROM blood_requests "
            "ORDER BY request_date DESC, request_id DESC"
        )
        rows = cur.fetchall()
        conn.close()

        if not rows:
            print("No requests have been recorded yet.")
            return

        print("-" * 74)
        print("{:<5}{:<20}{:<8}{:<8}{:<14}{}".format(
            "ID", "Patient", "Type", "Units", "Date", "Status"))
        print("-" * 74)
        for row in rows:
            print("{:<5}{:<20}{:<8}{:<8}{:<14}{}".format(*row))
        print("-" * 74)
        print("Total: {} request(s)".format(len(rows)))

    def distribution_log(self):
        """
        Which unit went to which patient, and when.
        This report joins THREE tables: issued_units, blood_requests, blood_units.
        """
        print("\n===== DISTRIBUTION LOG (issued blood) =====")
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT i.issue_date, r.patient_name, u.unit_id, u.blood_type "
            "FROM issued_units i "
            "JOIN blood_requests r ON i.request_id = r.request_id "
            "JOIN blood_units u ON i.unit_id = u.unit_id "
            "ORDER BY i.issue_date DESC, i.issue_id DESC"
        )
        rows = cur.fetchall()
        conn.close()

        if not rows:
            print("No blood has been issued yet.")
            return

        print("-" * 60)
        print("{:<14}{:<22}{:<10}{}".format(
            "Issued On", "Patient", "Unit", "Blood Type"))
        print("-" * 60)
        for issue_date, patient, unit_id, blood_type in rows:
            print("{:<14}{:<22}{:<10}{}".format(
                issue_date, patient, "#" + str(unit_id), blood_type))
        print("-" * 60)
        print("This answers the audit question: who received unit #X, and when?")
