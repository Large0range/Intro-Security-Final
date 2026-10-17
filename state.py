import threading
import zlib

logged_in = threading.Event();
logged_in.clear()

USER_INFO = {}
ADDED_CONTACTS = set()

FRIENDS = set()



RESET = "\x1b[0m"
DIM = "\x1b[2m"
BOLD = "\x1b[1m"
CYAN = "\x1b[36m"
RED = "\x1b[31m"

def color(text, code):
    return f"{code}{text}{RESET}"

def name_color(name, email):
    key = f"{name}:{email.lower()}".encode()
    return f"\x1b[38;5;{16 + zlib.crc32(key) % 216}m"


def output_to_console(message, text_color):
    print(f"{color(message, text_color)}")
