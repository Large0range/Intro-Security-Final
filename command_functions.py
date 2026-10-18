import json

from network import check_online, send_file, send_friend_request, send_message
from state import DIM, FRIENDS, color, name_color
from util import add_contact_to_dict


###########################################
# Prompts user for information
# Appends to people added by this user
# Sends request for connection to contact
###########################################
def add_contact():
    name = input("Enter Full Name: ")
    email = input("Enter Email Address: ")
    add_contact_to_dict(name, email)
    send_friend_request(name, email)



##########################################
# Lists contacts that have added the user back
# -- and are online
##########################################
def list_contact():
    if len(FRIENDS) == 0:
        print("No contacts found")
        return


    # Variable for formatting issues
    foundone = False
    print("Online Contacts:")

    for string_entry in FRIENDS:
        entry = json.loads(string_entry)
        online = check_online(entry['name'], entry['email'])
        if online:
            print(f"  {color(f'{entry['name']:<10}', name_color(entry['name'], entry['email']))}  {color(f'{entry['email']:<20}', DIM)} { "* Online" if online else "* Offline" }")
            foundone = True         # at least one person is online, set to true - we don't need formatting fix

    # If we have contacts in friends but they are not online
    # Avoids weird print formatting issues
    if not foundone:
        print("  No online contacts")


###########################################
# Prompts user for information
# Messages user if they are on friends list
###########################################
def message_contact():
    name = input("Enter Full Name: ")
    email = input("Enter Email Address: ")
    message = input("Enter Message: ")
    send_message(name, email, message)


###########################################
# Sends file to contact
# Prompts for name, email, and file path
###########################################
def send_file_contact():
    name = input("Enter Full Name: ")
    email = input("Enter Email Address: ")
    file_name = input("Enter File Path: ")
    send_file(name, email, file_name)
