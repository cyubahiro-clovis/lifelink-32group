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

def get_blood_type(message):
    # We keep asking them to type a valid bloodtype like in list blood_types above
    while True:
        answer = input(message).strip().upper()
        if answer in blood_types:
            return answer
        else:
            print("You typed a wrong blood type. Valid types include: A+, A-, B+, B-, AB+, AB-, O+, O- ")
            

def get_date(message, allow_blank=False):
    # Here we check that the user type a prper valid date in  YYYY-MM-DD format.
    # Or the user presses Enter and allow_blank=true

    while True:
        user_input = input(message).strip()
        if user_input == "" and allow_blank:
            return None
        try:
            return datetime.strptime(user_input, "%Y-%m-%d").date().isoformat()
        except ValueError:
            print("Invalid date. use the format YYYY-MM-DD, like 2024-07-12") 


def get_yes_no(message):
    # we keep asking the user to answer yes or no. and we return true for yes
    yes_lst = ["y", "yes"]
    no_lst = ["n", "no"]

    while True:
        answer = input(message + " (y/n): ").strip().lower()
        if answer in yes_lst:
            return True
        if answer in no_lst:
            return False
        print("Please answer y or n.")


def get_phone(message):
    #Making sure phone numbers are digits instead of letters
    while True:
        answer = input(message).strip()
        phone_number = answer.replace("+", "")
        if phone_number.isdigit() and 10 <= len(phone_number) <= 12:
            return answer
        print("Enter a valid phone number like 0789078235 or +250789078235")


def get_name(message):
    # making sure names are letters
    while True:
        answer = input(message).strip()
        if answer and answer.replace(" ", "").isalpha():
            return answer
        print("names should contain only letters")
