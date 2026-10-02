import json
import os
import bcrypt
from security import decrypt_fernet, encrypt_fernet, hash_password, init_crypt, verify_password



DATA_FILE = "user.json"
CONTACT_FILE = "contacts.json"

def user_exists():
    return os.path.isfile(DATA_FILE)

def register_user():
    name = input("Enter Full Name: ")
    email = input("Enter Email Address: ")
    password = hash_password(input("Enter Password: "))
    reenter = verify_password(input("Re-enter Password: "), password)

    salt = os.urandom(16)

    if reenter:
        info = {
            'name': name,
            'email': email,
            'password': password.decode(),
            'salt': salt.hex()
        }

        with open(DATA_FILE, "w") as file:
            json.dump(info, file)

        print("User Registered")
        print("Exiting Secure Drop")


def login_user():
    with open(DATA_FILE, "r") as file:
        data = json.load(file)

    email = input("Enter Email Address: ")
    password = input("Enter Password: ")
    salt = bytes.fromhex(data['salt'])

    init_crypt(password.encode(), salt)

    return verify_password(password, data['password'].encode()) and email == data['email']


def write_contact_to_file(name, email):
    person = {"name": name, "email": email}

    with open(CONTACT_FILE, "ab") as file:
        file.write(encrypt_fernet(str(person))+b'\n')


def read_all_contacts():
    contacts = []
    with open(CONTACT_FILE, "rb") as file:
        for entry in file.read().split(b'\n'):
            if entry == b'':
                break

            contacts.append(json.loads(decrypt_fernet(entry).decode().replace("\'", '\"')))

    return contacts
