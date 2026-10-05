import threading

logged_in = threading.Event();
logged_in.clear()

USER_INFO = {}
ADDED_CONTACTS = set()

FRIENDS = set()
