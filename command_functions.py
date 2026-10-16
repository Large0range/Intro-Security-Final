import json

from network import check_online, send_friend_request
from state import FRIENDS
from util import add_contact_to_dict


###########################################
# Prompts user for information
# Appends to people added by this user
# Sends request for connection to contact
# #########################################
def add_contact():
    name = input("Enter Full Name: ")
    email = input("Enter Email Address: ")
    add_contact_to_dict(name, email)
    send_friend_request(name, email)



##########################################
# Lists contacts that have added the user back, and are online
# ########################################
def list_contact():
    if len(FRIENDS) == 0:
        print("No contacts found")
        return


    # Variable for formatting issues
    foundone = False
    print("Online Contacts:")

    for string_entry in FRIENDS:
        entry = json.loads(string_entry)
        if check_online(entry['name'], entry['email']):
            print(f"  {entry['name']:<10}  {entry['email']:<20} { "* Online" if check_online(entry['name'], entry['email']) else "* Offline" }")
            foundone = True         # at least one person is online, set to true - we don't need formatting fix

    # If we have contacts in friends but they are not online
    #   Avoids weird print formatting issues
    if not foundone:
        print("  No online contacts")

def send_file():
    pass
