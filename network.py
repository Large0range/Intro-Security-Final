from ast import parse
import json
import os
from pathlib import Path
import socket
import queue
import sys
from threading import Thread
import threading

from Crypto.PublicKey import RSA

from security import decrypt_aes, decrypt_aes_secrets_verify, encrypt_aes, encrypt_generate_aes_secrets, generate_rsa_keys, read_keys_from_file, sign_message, verify_signature
from state import *


# Create shared queue per listener and sender threads
server_queue = queue.Queue()
RSA_PRIV = b""

# PROTOCOL TYPES
# Protocol for telling who person is
P_IAM = 1

# Protocol for sending friend request
P_REQUEST = 2

# Protocol for checking if person is online
P_PING = 3

# Message protocol -- not required but fun
P_MESSAGE = 7

# File protcol
P_FILE = 8

#Handshake Protocol
P_HANDS = 4

#Key Protocol
P_MYKEY = 5
P_OURAES = 6

# RESPONSE CODES
# Require response for protocol
P_RESPOND = 1
# No require response for protocol
P_NRESPOND = 0


# Error receive protocol
P_ERROR = 9
P_REMOVE = 0

# Default listener port
DEFAULT_SERVER_PORT = 65432

# Lookup dictionary for name to email and ip
table_lock = threading.Lock()

NAME_IP_TABLE = {}
IP_KEY_TABLE = {}

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

####################################################
# Takes other user's name and email and message
# Messages our friend securely
####################################################
def send_message(name, email, message):
    if not connect_to_friend(name, email, P_MESSAGE, P_NRESPOND, {'name': USER_INFO['name'], 'email': USER_INFO['email'], 'data': message}):
        output_to_console("Unable to Message User", RED + BOLD)

####################################################
# Takes other user's name and email and file path
# Sends file to user's computer
####################################################
def send_file(name, email, file_path):
    output_to_console("Sending file...", DIM)
    if not os.path.isfile(file_path):
        output_to_console("No file found", RED + BOLD)
        return

    with open(file_path, "rb") as file:
        data = file.read()
    if connect_to_friend(name, email, P_FILE, P_NRESPOND, {'name': USER_INFO['name'], 'email': USER_INFO['email'], 'file_path': file_path, 'data': zlib.compress(data, level=9).hex()}):
        output_to_console("File sent", DIM)
    else:
        output_to_console("Unable to Message User", RED + BOLD)



####################################################
# Takes other user's name and email
# Pings other user to see if their server is online
# -- Only happens if two are friends
####################################################
def check_online(name, email):
    return connect_to_friend(name, email, P_PING, P_NRESPOND, USER_INFO)


####################################################################
# Takes other user's name and email
# Takes protocl type and response code
# Takes payload to send to other user
# Returns:
#   True on proper send and lookup in IP Table
#   False if send was incorrect or name not in IP Table
####################################################################
def connect_to_user(name, email, type, respond_code, payload):
    try:
        # if name and email match then send payload -- prevents sending to wrong person with same name
        if name + ':' + email in NAME_IP_TABLE:
            return send_to_host(type, respond_code, payload, NAME_IP_TABLE[name + ':' + email])
    except KeyError:
        return False

    return False


####################################################################
# Takes other user's name and email --- explicit check if in friends
# Takes protocl type and response code
# Takes payload to send to other user
# Returns:
#   True on proper send and lookup in IP Table
#   False if send was incorrect or name not in IP Table
####################################################################
def connect_to_friend(name, email, type, respond_code, payload):
    try:
        # if name and email match then send payload -- prevents sending to wrong person with same name
        if name + ':' + email in NAME_IP_TABLE :
            return send_to_host_encrypted(type, respond_code, payload, NAME_IP_TABLE[name + ':' + email])
    except KeyError:
        return False

    return False


#################################################################################
# Startup a server that listens for all connections and recieves data from them
#################################################################################
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
                    # pull all sent data from the socket
                    data = b""
                    pull = conn.recv(4)
                    if len(pull) == 4:
                        length = int.from_bytes(pull, 'little')
                        data = conn.recv(length)


                        if length != len(data):
                            server_queue.put({'type': P_ERROR, 'data': {}, 'ip': addr[0]})
                            continue



                    # break if connection terminated
                    if data == b'':
                        break

                    # parse the data received into protocol type, response code, and payload associated
                    try:
                        dec = decrypt_aes(IP_KEY_TABLE[addr[0]][1], data)
                    except ValueError, KeyError:
                        dec = data

                    try:
                        type, response, payload = parse_bytes(dec)
                    except ValueError:
                        random_output_to_console("Error parsing data throwing out...", RED + BOLD)
                        continue

                    with open("data.log", "a") as file:
                        file.write(str(type) + " " + str(response) + " " + str(payload) + "\n")

                    try:
                        is_friend = json.dumps({'name': payload['name'], 'email': payload['email']}) in FRIENDS
                    except KeyError:
                        is_friend = False

                    # Special Protocol Types Require Server Action

                    # Store person in Name IP Table if they are telling us who they are
                    if type == P_IAM:
                        # Single key replacement atomic
                        NAME_IP_TABLE[payload['name'] + ':' + payload['email']] = addr[0]

                    if type == P_MYKEY:
                        if VERSION != payload['version']:
                            raise ValueError("Non matching versions... try updating to latest")
                        with table_lock:
                            IP_KEY_TABLE.setdefault(addr[0], [bytes.fromhex(payload['key']), None])
                            if IP_KEY_TABLE[addr[0]][0] == None:
                                IP_KEY_TABLE[addr[0]][0] = bytes.fromhex(payload['key'])


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

                        # if there was someone added remove them from added contacts
                        if r_contact != "":
                            ADDED_CONTACTS.remove(r_contact)

                    if type == P_ERROR:
                        random_output_to_console("Error sending message, maybe try again?", RED + BOLD)

                    if type == P_REMOVE:
                        FRIENDS.remove(json.dumps({'name': payload['name'], 'email': payload['email']}))

                    # Friend protocols
                    if type == P_PING and not is_friend:
                        server_queue.put({'type': P_REMOVE, 'data': USER_INFO, 'ip': addr[0]})

                    # Message protocol from friend
                    if type == P_MESSAGE and is_friend:
                        person_specific_output(payload['name'], payload['email'], payload['data'])

                    # File sending protocol
                    if type == P_FILE and is_friend:
                        # Decompress the bytes from the payload
                        bytedata = bytes.fromhex(payload['data'])
                        uncompressed = zlib.decompress(bytedata).decode()

                        # Gut the file path, only write to Data folder
                        full_path = Path(payload['file_path'])
                        with open('Data/' + full_path.name, "w") as file:
                            file.write(uncompressed)

                        person_specific_output(payload['name'], payload['email'], "File" + full_path.name + " Received")

                    # if response code is 1 then response
                    if response == P_RESPOND:
                        server_queue.put({'type': type, 'data': payload, 'ip': addr[0]})


######################################################################
# Startup a continuous thread to service items in the shared queue
######################################################################
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
            send_to_host_encrypted(P_IAM, P_NRESPOND, USER_INFO, item['ip'])

        # If we need to confirm add back of friend request
        # -- Send with no response and payload of user info
        # !- Separated from P_IAM for semantics and readability
        if item['type'] == P_REQUEST:
            send_to_host_encrypted(P_REQUEST, P_NRESPOND, USER_INFO, item['ip'])

        # If we recieved the public key then encrypt and send them aes key
        if item['type'] == P_MYKEY:
            with table_lock:
                rsa_pub = IP_KEY_TABLE[item['ip']][0]

            session_key, nonce, tag, cipher_text, real_key = encrypt_generate_aes_secrets(rsa_pub, str(USER_INFO).encode())

            IP_KEY_TABLE[item['ip']][1] = real_key

            send_to_host(P_OURAES, P_RESPOND, {'session_key': session_key.hex(), 'nonce': nonce.hex(), 'tag': tag.hex(), 'ciphertext': cipher_text.hex()}, item['ip'])

        # If we have recieved an AES key then decrypt with our RSA priv
        # Process data then send signature to authenticate who we are
        # -- Auth can be used at any time to double check
        if item['type'] == P_OURAES:
            payload = item['data']

            plaintext, aes_key = decrypt_aes_secrets_verify(RSA_PRIV, bytes.fromhex(payload['session_key']), bytes.fromhex(payload['nonce']), bytes.fromhex(payload['tag']), bytes.fromhex(payload['ciphertext']))
            with table_lock:
                IP_KEY_TABLE.setdefault(item['ip'], [None, aes_key])
                if IP_KEY_TABLE[item['ip']][1] == None:
                    IP_KEY_TABLE[item['ip']][1] = aes_key

            _, signature = sign_message(RSA_PRIV, plaintext)

            send_to_host(P_HANDS, P_RESPOND, {'signature': signature.hex()}, item['ip'])


        # Final process of the handshake, we need to authenticate they are the person
        # Auth them, tell them who we are definitively. Tunnel created between
        if item['type'] == P_HANDS:
            payload = item['data']
            verified = verify_signature(IP_KEY_TABLE[item['ip']][0], str(USER_INFO).encode(), bytes.fromhex(payload['signature']))
            if verified:
                send_to_host_encrypted(P_IAM, P_RESPOND, USER_INFO, item['ip'])
            else:
                output_to_console("Could Not Verify Hash", RED + BOLD)


        # If we did not receive all the bytes tell the sender
        if item['type'] == P_ERROR:
            send_to_host_encrypted(P_ERROR, P_NRESPOND, {}, item['ip'])

        if item['type'] == P_REMOVE:
            send_to_host_encrypted(P_REMOVE, P_NRESPOND, item['data'], item['ip'])

        # Mark queue item as finished
        server_queue.task_done()

###########################################################
# Sends payload to host
# Takes protocol type, response, payload, and host
# Returns True on successful transmission
###########################################################
def send_to_host(type: int, response: int, payload: dict, host: str) -> bool:
    return transmit_payload((str(type)+str(response)+json.dumps(payload)).encode(), host)

###########################################################
# Sends payload encrypted to host
# Takes protocol type, response, payload, and host
# Returns True on successful transmission
###########################################################
def send_to_host_encrypted(type: int, response: int, payload: dict, host: str) -> bool:
    enc_data = encrypt_aes(IP_KEY_TABLE[host][1], (str(type)+str(response)+json.dumps(payload)).encode())
    return transmit_payload(enc_data, host)

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

############################################
# Send information to host
# Takes data to transmit        - bytes
# Takes host                    - string
# Returns:
#   True on successful transmission
#   False on connection refused
############################################
def transmit_payload(info: bytes, host: str):
    # Define the server's IP address and port to connect to
    server_host = host

    # socket.AF_INET specifies IPv4, socket.SOCK_STREAM specifies TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.settimeout(1)
            client_socket.connect((server_host, DEFAULT_SERVER_PORT))

            client_socket.sendall(len(info).to_bytes(4, 'little'))

            client_socket.sendall(info)

        except ConnectionRefusedError, TimeoutError:
            return False


    return True

#############################################################
# Startup the network threads and tell people we are online
# Takes user information            - dict
# Takes reference to thread list    - list
#############################################################
def startup_network(info, network_threads):
    global RSA_PRIV

    #I AM PROTOCOL
    if os.path.isfile("rsa.pem"):
        print("Grabbing One Way Keys")
        priv, pub = read_keys_from_file()
    else:
        print("Generating One Way Keys")
        priv, pub = generate_rsa_keys()

    RSA_PRIV = priv

    print("Keys Grabbed")

    server_thread = Thread(target=text_me_back_protocol)
    response_thread = Thread(target=respond_to_dms)

    server_thread.start()
    response_thread.start()

    for ip in IPS:
        send_to_host(P_MYKEY, P_RESPOND, {"version": VERSION, "key": pub.hex()}, ip)


    network_threads.append(server_thread)
    network_threads.append(response_thread)
