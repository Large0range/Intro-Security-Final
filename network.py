import json
import socket
import queue
from threading import Thread

from state import logged_in


server_data = queue.Queue()


DEFAULT_SERVER_PORT = 65432
DEFAULT_CLIENT_PORT = 65431

NAME_IP_TABLE = {}
IPS = ["10.0.0.2"]

def send_friend_request(name, email):
    connect_to_friend(name, email)
    if get_friend_response(name, email):
        print("Accepted")



#Fake Friend Protocol
def connect_to_friend(name, email):
    print(NAME_IP_TABLE)
    try:
        print(NAME_IP_TABLE[name])
    except KeyError:
        return

def get_friend_response(name, email):
    return True



def text_me_back_protocol():
    server_host = '10.0.0.1'

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        # Allow immediate reuse of the port after stopping the server (prevents "Address already in use" errors)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the socket to the host and port
        server_socket.bind((server_host, DEFAULT_SERVER_PORT))

        # Enable the server to accept connections
        server_socket.listen()
        print(f"Server is listening on {server_host}:{DEFAULT_SERVER_PORT}...")

        logged_in.wait()
        server_socket.settimeout(1.0)
        while logged_in.is_set():
            # Wait for an incoming client connection
            try:
                conn, addr = server_socket.accept()
                conn.settimeout(1.0)
            except TimeoutError:
                continue

            print(conn)
            # Use a context manager to ensure the client connection closes cleanly
            with conn:
                print(f"Connected successfully to client: {addr}")

                while True:
                    # GET RESPONSES FROM PEOPLE
                    data = conn.recv(1024)
                    if data == b'':
                        break

                    message = data.decode()
                    if message.startswith("IAM"):
                        payload = json.loads(message.replace("IAM", "").replace("\'", '\"'))
                        NAME_IP_TABLE[payload['name']] = {'email': payload['email'], 'ip': addr[0]}


#Returns the information of the person at the host and port
def i_am_protocol(info, host, port):
    # Define the server's IP address and port to connect to
    server_host = host  # 'localhost' for testing on the same machine
    server_port = port         # Must match the server's listening port



    # 1. Create a socket object
    # socket.AF_INET specifies IPv4, socket.SOCK_STREAM specifies TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            # 2. Connect to the server
            client_socket.connect((server_host, server_port))
            print(f"Connected successfully to {server_host}:{server_port}")

            # 4. Receive data from the server
            # 1024 is the buffer size (max bytes to receive at once)
            client_socket.sendall(str(info).encode())

        except ConnectionRefusedError:
            print(f"Failed to connect. Is the server running on port {server_port}?")
        except Exception as e:
            print(f"An error occurred: {e}")


#Send out we are online
def startup_network(info, network_threads):
    thread = Thread(target=text_me_back_protocol)
    thread.start()

    for ip in IPS:
        i_am_protocol(info, ip, DEFAULT_SERVER_PORT)

    network_threads.append(thread)



#Build lookup table
#def build_lookup_table():
#    for ip in IPS:
#        response = who_you_protocol(ip, DEFAULT_SERVER_PORT)
#        NAME_IP_TABLE[response[0]] = {'email': response[1], 'ip': response[2]}
