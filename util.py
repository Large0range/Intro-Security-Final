import json
import os

from cryptography.fernet import InvalidToken
from security import decrypt_fernet, encrypt_fernet, hash_password, init_crypt, verify_password
from state import ADDED_CONTACTS, FRIENDS


# Storage files
DATA_FILE = "user.bin"
CONTACT_FILE = "contacts.bin"


###################################################################
# Check if user exists
# Returns True if they do
###################################################################
def user_exists():
    return os.path.isfile(DATA_FILE)



###################################################################
# Register user, prompts for name email and password
# Salts and initializes crypt
# Writes to base data file
###################################################################
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
            file.write(encrypt_fernet(json.dumps(info)) + b'\n' + salt.hex().encode())

        print("User Registered")
        print("Exiting Secure Drop")



###################################################################
# Login user, takes a dictionary of user information to output to
# Reads base data file and writes to user info dictionary
###################################################################
def login_user(user_info):
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



    user_info['name'] = data['name']
    user_info['email'] = data['email']


    return verify_password(password, data['password'].encode()) and email == data['email']



###################################################################
# Takes a name and email
# Writes to the set of people we have added
# -- prevents double add
###################################################################
def add_contact_to_dict(name, email):
    person = {"name": name, "email": email}

    ADDED_CONTACTS.add(json.dumps(person))


###################################################################
# Writes encrypted friend data to a contact file
###################################################################
def write_contacts_to_file():
    writelines = []
    for contact in FRIENDS:
        writelines.append(encrypt_fernet(contact) + b'\n')

    with open(CONTACT_FILE, "wb") as file:
        file.writelines(writelines)



###################################################################
# Reads all contacts from the friend file
# Adds them to friend dictionary
###################################################################
def read_all_contacts_from_file():
    if not os.path.isfile(CONTACT_FILE):
        return

    with open(CONTACT_FILE, "rb") as file:
        for entry in file.read().split(b'\n'):
            if entry == b'':
                break

            FRIENDS.add(decrypt_fernet(entry).decode())



###################################################################
# Helper function decodes bytes and converts to dictionary
###################################################################
def convert_byte_to_json(bytestring):
    return json.loads(bytestring.decode().replace("\'", '\"'))
