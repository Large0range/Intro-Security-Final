import json
import socket
import queue
import sys
from threading import Thread

from state import ADDED_CONTACTS, FRIENDS, USER_INFO, logged_in

# Create shared queue per listener and sender threads
server_queue = queue.Queue()

# PROTOCOL TYPES
# Protocol for telling who person is
P_IAM = 1

# Protocol for sending friend request
P_REQUEST = 2

# Protocol for checking if person is online
P_PING = 3

# RESPONSE CODES
# Require response for protocol
P_RESPOND = 1
# No require response for protocol
P_NRESPOND = 0


# Default listener port
DEFAULT_SERVER_PORT = 65432

# Lookup dictionary for name to email and ip
NAME_IP_TABLE = {}

#########################################################################
# REMOVE IN IMPLEMENTATION
# Dummy code for simulating multiple machines
IPS = [sys.argv[2]]
SERVER_HOST = sys.argv[1]
print(sys.argv[1], sys.argv[2])
#########################################################################

##########################
# Takes other user's name and email
# Tells other user we have added them and gives our user info
##########################
def send_friend_request(name, email):
    connect_to_friend(name, email, P_REQUEST, P_NRESPOND, USER_INFO)


##########################
# Takes other user's name and email
# Pings other user to see if their server is online
# -- Only happens if two are friends
#########################
def check_online(name, email):
    return connect_to_friend(name, email, P_PING, P_NRESPOND, {})


####################################################################
# Takes other user's name and email
# Takes protocl type and response code
# Takes payload to send to other user
# Returns:
#   True on proper send and lookup in IP Table
#   False if send was incorrect or name not in IP Table
####################################################################
def connect_to_friend(name, email, type, respond_code, payload):
    try:
        # if name and email match then send payload -- prevents sending to wrong person with same name
        if NAME_IP_TABLE[name]['email'] == email:
            return send_to_host(type, respond_code, payload, NAME_IP_TABLE[name]['ip'])
    except KeyError:
        return False

    return False


#################################################
# Startup a server that listens for all connections and recieves data from them
#################################################
def text_me_back_protocol():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        # Allow immediate reuse of the port after stopping the server (prevents "Address already in use" errors)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the socket to the host and port
        server_socket.bind((SERVER_HOST, DEFAULT_SERVER_PORT))

        # Enable the server to accept connections
        server_socket.listen()
        print(f"Server is listening on {SERVER_HOST}:{DEFAULT_SERVER_PORT}...")

        # If we are not logged in, wait for it
        logged_in.wait()

        # Set server accept timeout for 1 second
        server_socket.settimeout(1.0)
        while logged_in.is_set():
            # Wait for an incoming user connection
            try:
                conn, addr = server_socket.accept()

                # set connection recv timeout 1 second
                conn.settimeout(1.0)
            except TimeoutError:
                continue

            with conn:
                # loop infinitely to talk as much as we need
                while True:
                    # get data from
                    data = conn.recv(1024)

                    # break if connection terminated
                    if data == b'':
                        break

                    # parse the data received into protocol type, response code, and payload associated
                    type, response, payload = parse_bytes(data)

                    #################################################
                    # REMOVE IN IMPLEMENTATION
                    print("Recieved", type, response, payload)
                    #################################################

                    # Special Protocol Types Require Server Action

                    # Store person in Name IP Table if they are telling us who they are
                    if type == P_IAM:
                        NAME_IP_TABLE[payload['name']] = {'email': payload['email'], 'ip': addr[0]}

                    # If person sent us a friend request check if we have them in our friends
                    # -- Required to send back proper message
                    if type == P_REQUEST:
                        r_contact = ""
                        jpay = json.dumps(payload)
                        for contact in ADDED_CONTACTS:
                            # If we have added them as well
                            if jpay == contact:
                                # Set variable to remove from added contacts
                                r_contact = contact

                                # Add them to friends set
                                FRIENDS.add(contact)

                                # Inform them that we have also added them back
                                server_queue.put({'type': P_REQUEST, 'data': payload, 'ip': addr[0]})

                            #################################################
                            # REMOVE IN IMPLEMENTATION
                            print("listed contact", contact)
                            #################################################

                        # if there was someone added remove them from added contacts
                        if r_contact != "":
                            ADDED_CONTACTS.remove(r_contact)


                    # if response code is 1 then response
                    if response == P_RESPOND:
                        server_queue.put({'type': type, 'data': payload, 'ip': addr[0]})



####################################
# Startup a continuous thread to service items in the shared queue
####################################
def respond_to_dms():
    # wait till we are logged in
    logged_in.wait()
    while logged_in.is_set():
        # get something and wait if there is nothing
        item = {}
        try:
            item = server_queue.get(False, 1.0)
        except queue.Empty:
            continue

        # Protocol response handlers

        # If we need to tell person who we are
        # -- Send with no response and payload of user info
        if item['type'] == P_IAM:
            #transmit_payload((str(P_IAM) + json.dumps(USER_INFO)).encode(), item['ip'])
            send_to_host(P_IAM, P_NRESPOND, USER_INFO, item['ip'])

        # if we need to confirm add back of friend request
        # -- Send with no response and payload of user info
        # !- Separated from P_IAM for semantics and readability
        if item['type'] == P_REQUEST:
            send_to_host(P_REQUEST, P_NRESPOND, USER_INFO, item['ip'])

        # Mark queue item as finished
        server_queue.task_done()

#################################################
# Sends payload to host
# Takes protocol type, response, payload, and host
# Returns True on successful transmission
#################################################
def send_to_host(type: int, response: int, payload: dict, host: str) -> bool:
    return transmit_payload((str(type)+str(response)+json.dumps(payload)).encode(), host)

################################################
# Parse received bytes in listener
# Takes a bytestring of data from other user
# Returns:
#   Protocol type           - bytes
#   Response                - bytes
#   Rayload                 - bytes
################################################
def parse_bytes(bytestring: bytes):
    full_text = bytestring.decode()
    type = int(full_text[:1])
    response = int(full_text[1:2])
    payload = json.loads(full_text[2:])

    return type, response, payload

#######################################
# Send information to host
# Takes data to transmit        - bytes
# Takes host                    - string
# Returns:
#   True on successful transmission
#   False on connection refused
def transmit_payload(info: bytes, host: str):
    # Define the server's IP address and port to connect to
    server_host = host

    # socket.AF_INET specifies IPv4, socket.SOCK_STREAM specifies TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((server_host, DEFAULT_SERVER_PORT))

            client_socket.sendall(info)

        except ConnectionRefusedError:
            return False


    return True


#############################################################
# Startup the network threads and tell people we are online
# Takes user information            - dict
# Takes reference to thread list    - list
#############################################################
def startup_network(info, network_threads):
    server_thread = Thread(target=text_me_back_protocol)
    response_thread = Thread(target=respond_to_dms)

    server_thread.start()
    response_thread.start()

    #I AM PROTOCOL
    for ip in IPS:
        send_to_host(P_IAM, P_RESPOND, info, ip)

    network_threads.append(server_thread)
    network_threads.append(response_thread)
