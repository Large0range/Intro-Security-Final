#!/usr/bin/env python3

import sys
from network import startup_network
from util import login_user, read_all_contacts_from_file, user_exists, register_user, write_contacts_to_file
from command_functions import *

from state import logged_in, USER_INFO


network_threads = []

def test():
    print("hello")

commands = {
    "test": [test, "This is a test command for scalability"],
    "add": [add_contact, "Adds a new contact to your contact list"],
    "list": [list_contact, "Lists your stored contacts"],
    "send": [send_file, "Sends a file to a contact"],
    "exit": [lambda: 0, "Exits the Secure Drop Application"]
}

if user_exists():
    if login_user(USER_INFO):
        # on login setup
        logged_in.set()
        startup_network(USER_INFO, network_threads) # send out my payload
        read_all_contacts_from_file()

        print("User logged in")
        print("Welcome to Secure Drop")
        print("Type help for a list of commands")
        print()

    else:
        print("Invalid Login")
else:
    print("No users registered for this client")

    if (input("Do you want to register a new user (y/n)? ") == 'y'):
        register_user()
    else:
        sys.exit(1)


while logged_in.is_set():
    command = input(">")

    if command == "exit":
        print("Exiting Secure Drop")
        logged_in.clear()

    elif command == "help":
        for i in commands:
            print(i + ":", commands[i][1])

    else:
        try:
            commands[command][0]()
        except KeyError:
            print("Not a command")

        print()



write_contacts_to_file()

for thread in network_threads:
    thread.join()
