from security import decrypt_fernet
from util import read_all_contacts, write_contact_to_file


def add_contact():
    name = input("Enter Full Name: ")
    email = input("Enter Email Address: ")
    write_contact_to_file(name, email)

def list_contact():
    for entry in read_all_contacts():
        print(entry['name'])

def send_file():
    pass
