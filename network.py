import json
import socket
import queue
import sys
from threading import Thread

from state import ADDED_CONTACTS, FRIENDS, USER_INFO, logged_in


server_queue = queue.Queue()

# PROTOCOL TYPES
P_IAM = 1
P_REQUEST = 2
P_PING = 3

P_RESPOND = 0
P_NRESPOND = 1

DEFAULT_SERVER_PORT = 65432
DEFAULT_CLIENT_PORT = 65431

NAME_IP_TABLE = {}
IPS = [sys.argv[2]]

SERVER_HOST = sys.argv[1]
print(sys.argv[1], sys.argv[2])

def send_friend_request(name, email):
    connect_to_friend(name, email, P_REQUEST, P_NRESPOND, USER_INFO)


def check_online(name, email):
    return connect_to_friend(name, email, P_PING, P_NRESPOND, {})


#Send to person based on name and email, with type, requiring response and final payload
def connect_to_friend(name, email, type, respond_code, payload):
    try:
        if NAME_IP_TABLE[name]['email'] == email:
            #print(f"Correct Person, Sending Type and Payload {type} {payload}")
            return send_to_host(type, respond_code, payload, NAME_IP_TABLE[name]['ip'])
            #transmit_payload((str(P_REQUEST) + json.dumps(USER_INFO)).encode(), NAME_IP_TABLE[name]['ip'])
    except KeyError:
        return False

    return False




def text_me_back_protocol():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        # Allow immediate reuse of the port after stopping the server (prevents "Address already in use" errors)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the socket to the host and port
        server_socket.bind((SERVER_HOST, DEFAULT_SERVER_PORT))

        # Enable the server to accept connections
        server_socket.listen()
        print(f"Server is listening on {SERVER_HOST}:{DEFAULT_SERVER_PORT}...")

        logged_in.wait()
        server_socket.settimeout(1.0)
        while logged_in.is_set():
            # Wait for an incoming client connection
            try:
                conn, addr = server_socket.accept()
                conn.settimeout(1.0)
            except TimeoutError:
                continue

            # Use a context manager to ensure the client connection closes cleanly
            with conn:
                #print(f"Connected successfully to client: {addr}")

                while True:
                    # GET RESPONSES FROM PEOPLE
                    data = conn.recv(1024)
                    if data == b'':
                        break

                    type, response, payload = parse_bytes(data)

                    print("Recieved", type, response, payload)

                    if type == P_IAM:
                        NAME_IP_TABLE[payload['name']] = {'email': payload['email'], 'ip': addr[0]}

                    if type == P_REQUEST:
                        r_contact = ""
                        for contact in ADDED_CONTACTS:
                            if json.dumps(payload) == contact:
                                r_contact = contact
                                FRIENDS.add(contact)

                                server_queue.put({'type': P_RESPOND, 'data': payload, 'ip': addr[0]})

                            print("listed contact", contact)

                        if r_contact != "":
                            ADDED_CONTACTS.remove(r_contact)

                    if response == P_RESPOND:
                        server_queue.put({'type': type, 'data': payload, 'ip': addr[0]})



# Response to recieved requests from clients
def respond_to_dms():
    logged_in.wait()
    while logged_in.is_set():
        item = {}
        try:
            item = server_queue.get(False, 1.0)
        except queue.Empty:
            continue

        if item['type'] == P_IAM:
            #transmit_payload((str(P_IAM) + json.dumps(USER_INFO)).encode(), item['ip'])
            send_to_host(P_IAM, P_NRESPOND, USER_INFO, item['ip'])

        if item['type'] == P_RESPOND:           # P_RESPOND is a Non Responsive protocol -- this can only be reached if we have added this person, confirmation of add
            send_to_host(P_REQUEST, P_NRESPOND, USER_INFO, item['ip'])

        server_queue.task_done()


def send_to_host(type: int, response: int, payload: dict, host: str):
    return transmit_payload((str(type)+str(response)+json.dumps(payload)).encode(), host)

def parse_bytes(bytestring: bytes):
    full_text = bytestring.decode()
    type = int(full_text[:1])
    response = int(full_text[1:2])
    payload = json.loads(full_text[2:])

    return type, response, payload

#Sends string payload to host address
def transmit_payload(info: bytes, host):
    # Define the server's IP address and port to connect to
    server_host = host  # 'localhost' for testing on the same machine

    # 1. Create a socket object
    # socket.AF_INET specifies IPv4, socket.SOCK_STREAM specifies TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            # 2. Connect to the server
            client_socket.connect((server_host, DEFAULT_SERVER_PORT))
            #print(f"Connected successfully to {server_host}:{DEFAULT_SERVER_PORT}")

            # 4. Receive data from the server
            # 1024 is the buffer size (max bytes to receive at once)
            client_socket.sendall(info)

        except ConnectionRefusedError:
            return False


    return True


#Send out we are online
def startup_network(info, network_threads):
    server_thread = Thread(target=text_me_back_protocol)
    response_thread = Thread(target=respond_to_dms)

    server_thread.start()
    response_thread.start()

    #I AM PROTOCOL
    for ip in IPS:
        send_to_host(P_IAM, P_RESPOND, info, ip)
        #transmit_payload((str(P_IAM) + json.dumps(info)).encode(), ip)

    network_threads.append(server_thread)
    network_threads.append(response_thread)



#Build lookup table
#def build_lookup_table():
#    for ip in IPS:
#        response = who_you_protocol(ip, DEFAULT_SERVER_PORT)
#        NAME_IP_TABLE[response[0]] = {'email': response[1], 'ip': response[2]}
