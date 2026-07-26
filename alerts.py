#!/usr/bin/python3
"""
alerts.py is the alert engine.

In our PLP-1 architecture diagrama promised an Alert Engine  with low stock warningsand expiry notifications. Expiry notifications live in inventory.py;
the low stock warnings live here, together with the dashboard the user sees the moment the application starts.
"""

from datetime import date, timedelta

from database import BaseManager
from validators import blood_types

class AlertEngine(BaseManager):
    """Warns staff before a shortage or a wastage happens."""

    LOW_STOCK_THRESHOLD = 5
    EXPIRY_WARNING_DAYS = 7
    
    def low_stock_alert(self):
        """Warn about blood types that are running low or are out of stock."""
        print("\n-- Low Stock Alert --")
        today = date.today().isoformat()

        conn = self.connect()
        cur = conn.cursor()

        warnings = 0
        for blood_type in blood_types:
            cur.execute(
                    "SELECT COUNT(*) FROM blood_units "
                "WHERE status = 'available' AND expiry_date >= ? "
                "AND blood_type = ?",
                (today, blood_type),
            )
            count = cur.fetchone()[0]

            if count == 0:
                print("  OUT OF STOCK: {} - 0 units available!".format(blood_type))
                warnings += 1
            elif count < self.LOW_STOCK_THRESHOLD:
                print("  LOW STOCK: only {} unit(s) of {} left "
                      "(threshold is {}).".format(
                          count, blood_type, self.LOW_STOCK_THRESHOLD))
                warnings += 1
        conn.close()

        if warnings == 0:
            print("Stock levels are healthy for all 8 blood types.")
        else:
            print("\n{} blood type(s) need attention.".format(warnings))
            print("Tip: use Donor Management > Find eligible donors "
                  "to get a call list.")

    def startup_summary(self):
        """The small dashboard shown every time the application starts."""
        today = date.today()
        week = today + timedelta(days=self.EXPIRY_WARNING_DAYS)

        conn = self.connect()
        cur = conn.cursor()

        cur.execute(
            "SELECT COUNT(*) FROM blood_units "
            "WHERE status = 'available' AND expiry_date >= ?",
            (today.isoformat(),),
        )
        available = cur.fetchone()[0]

        cur.execute(
            "SELECT COUNT(*) FROM blood_units "
            "WHERE status = 'available' AND expiry_date >= ? AND expiry_date <= ?",
            (today.isoformat(), week.isoformat()),
        )
        expiring = cur.fetchone()[0]

        cur.execute(
            "SELECT COUNT(*) FROM blood_requests WHERE status = 'pending'")
        pending = cur.fetchone()[0]
        conn.close()

        print("-" * 52)
        print(" TODAY ({}) ".format(today.isoformat()))
        print(" {} unit(s) in stock | {} expiring within {} days | "
              "{} pending request(s)".format(
                  available, expiring, self.EXPIRY_WARNING_DAYS, pending))
        print("-" * 52)
        if expiring > 0:
            print(" ACTION NEEDED: go to Blood Inventory > Check blood "
                  "expiry dates today!")
        if pending > 0:
            print(" {} request(s) are waiting for approval.".format(pending))
