import json
import os

from cryptography.fernet import InvalidToken
from security import decrypt_fernet, encrypt_fernet, hash_password, init_crypt, verify_password



DATA_FILE = "user.bin"
CONTACT_FILE = "contacts.bin"

def user_exists():
    return os.path.isfile(DATA_FILE)

def register_user():
    name = input("Enter Full Name: ")
    email = input("Enter Email Address: ")
    password = input("Enter Password: ")
    reenter = verify_password(input("Re-enter Password: "), hash_password(password))

    salt = os.urandom(16)

    init_crypt(password.encode(), salt)

    if reenter:
        info = {
            'name': name,
            'email': email,
            'password': hash_password(password).decode(),
            'salt': salt.hex()
        }

        with open(DATA_FILE, "wb") as file:
            file.write(encrypt_fernet(str(info)) + b'\n' + salt.hex().encode())

        print("User Registered")
        print("Exiting Secure Drop")


def login_user():
    with open(DATA_FILE, "rb") as file:
        a = file.read().split(b'\n')
        salt = a[1]

    email = input("Enter Email Address: ")
    password = input("Enter Password: ")
    salt = bytes.fromhex(salt)

    init_crypt(password.encode(), salt)

    try:
        with open(DATA_FILE, "rb") as file:
            data = convert_byte_to_json(decrypt_fernet(file.read().split(b'\n')[0]))
    except InvalidToken:
        return False

    return verify_password(password, data['password'].encode()) and email == data['email']


def write_contact_to_file(name, email):
    person = {"name": name, "email": email}

    with open(CONTACT_FILE, "ab") as file:
        file.write(encrypt_fernet(str(person))+b'\n')


def read_all_contacts():
    contacts = []
    if not os.path.isfile(CONTACT_FILE):
        return contacts

    with open(CONTACT_FILE, "rb") as file:
        for entry in file.read().split(b'\n'):
            if entry == b'':
                break

            contacts.append(convert_byte_to_json(decrypt_fernet(entry)))

    return contacts


def convert_byte_to_json(bytestring):
    return json.loads(bytestring.decode().replace("\'", '\"'))
