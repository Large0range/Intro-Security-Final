import json

from network import send_friend_request
from state import FRIENDS
from util import add_contact_to_dict



def add_contact():
    name = input("Enter Full Name: ")
    email = input("Enter Email Address: ")
    add_contact_to_dict(name, email)
    send_friend_request(name, email)

def list_contact():
    if len(FRIENDS) == 0:
        print("No contacts found")
        return

    for string_entry in FRIENDS:
        entry = json.loads(string_entry)
        print(entry['name'], "  ", entry['email'])

def send_file():
    pass
