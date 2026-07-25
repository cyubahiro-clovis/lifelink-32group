#!/usr/bin/python3
"""
This py file contains functions that help us detect bad inputs that would
crash the program. These inputs like letters where the program expects numbers
or wrong blood types like C+ and wrong date
"""

from datetime import datetime

blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

def get_nonempty(message):
    # keep asking the user to type something instead of leaving it empty
    while True:
        answer = input(message).strip()
        if answer:
            return answer
        else:
            print("Please type something. You left it blank")


def get_int(message, minimum=None):
    # this helps us to detect that user isn't typing a whole number like text or 4.5
    while True:
        user_input = input(message).strip()
        try:
            answer = int(user_input)
        except ValueError:
            print("Enter a whole number like 2 or 3")
            continue
        if minimum is not None and answer < minimum:
            print(f"Please enter a number that is atleast {minimum}")
            continue
        return answer


