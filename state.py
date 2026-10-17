import threading
import zlib

# Threading events needed across program
logged_in = threading.Event();
logged_in.clear()

# Version of program
VERSION = 2.0


# User and contact information
USER_INFO = {}
ADDED_CONTACTS = set()

FRIENDS = set()


# Console output coloring
RESET = "\x1b[0m"
DIM = "\x1b[2m"
BOLD = "\x1b[1m"
CYAN = "\x1b[36m"
RED = "\x1b[31m"


###################################################################
# Takes a message to output and a color code
# Returns a colored message
###################################################################
def color(text, code):
    return f"{code}{text}{RESET}"



###################################################################
# Takes a name and email
# Returns a hashed color from the email for name
# -- For variety
###################################################################
def name_color(name, email):
    key = f"{name}:{email.lower()}".encode()
    return f"\x1b[38;5;{16 + zlib.crc32(key) % 216}m"


###################################################################
# Takes a message and a desired color for message
# Correctly outputs to the console
###################################################################
def output_to_console(message, text_color):
    print(f"{color(message, text_color)}")
