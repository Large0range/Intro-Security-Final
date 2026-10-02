import sys
from util import login_user, user_exists, register_user
from command_functions import *

logged_in = False

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
    if login_user():
        print("User logged in")
        print("Welcome to Secure Drop")
        print("Type help for a list of commands")
        print()

        logged_in = True
    else:
        print("Invalid Login")
else:
    print("No users registered for this client")

    if (input("Do you want to register a new user (y/n)? ") == 'y'):
        register_user()
    else:
        sys.exit(1)


while logged_in:
    command = input(">")

    if command == "exit":
        print("Exiting Secure Drop")
        logged_in = False

    elif command == "help":
        for i in commands:
            print(i + ":", commands[i][1])

    else:
        try:
            commands[command][0]()
        except KeyError:
            print("Not a command")

        print()
