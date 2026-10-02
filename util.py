import json
import os
from textwrap import indent

import bcrypt

from security import hash_password, verify_password


DATA_FILE = "user.json"
CONTACT_FILE = "contacts.json"

def user_exists():
    return os.path.isfile(DATA_FILE)

def register_user():
    name = input("Enter Full Name: ")
    email = input("Enter Email Address: ")
    password = hash_password(input("Enter Password: "))
    reenter = bcrypt.checkpw(input("Re-enter Password: ").encode('utf-8'), password)

    if reenter:
        info = {
            'name': name,
            'email': email,
            'password': password.decode()
        }

        with open(DATA_FILE, "w") as file:
            json.dump(info, file, indent=4)

        print("User Registered")
        print("Exiting Secure Drop")


def login_user():
    with open(DATA_FILE, "r") as file:
        data = json.load(file)

    email = input("Enter Email Address: ")
    password = input("Enter Password: ")

    return verify_password(password, data['password'].encode()) and email == data['email']


def store_contact(name, email):
    person = {"name": name, "email": email}

    with open(CONTACT_FILE, "a") as file:
        json.dump(person, file, indent=4)
