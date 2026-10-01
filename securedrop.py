from util import login_user, user_exists, register_user
import sys

if user_exists():
    if login_user():
        print("User logged in")
    else:
        print("what")
else:
    print("No users registered for this client")

    if (input("Do you want to register a new user (y/n)? ") == 'y'):
        register_user()
    else:
        sys.exit(1)
