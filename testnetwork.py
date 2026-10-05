#!/usr/bin/env python3

import json
import socket
from threading import Thread
import queue as QUEUE

queue = QUEUE.Queue()


whoami = {
    "name": "Alexander Roy",
    "email": "root"
}

# Define host and port
# '0.0.0.0' listens on all available network interfaces (local network + localhost)
# Use '127.0.0.1' if you only want to allow connections from the same machine
HOST = "10.0.0.2"
PORT = 65432  # Choose any non-privileged port (> 1023)

IP_LOOKUP = {}


def convert_byte_to_json(bytestring):
    return json.loads(bytestring.decode().replace("\'", '\"'))




# Create a TCP/IP socket
# socket.AF_INET specifies IPv4; socket.SOCK_STREAM specifies TCP
def setup_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        # Allow immediate reuse of the port after stopping the server (prevents "Address already in use" errors)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the socket to the host and port
        server_socket.bind((HOST, PORT))

        # Enable the server to accept connections
        server_socket.listen()
        print(f"Server is listening on {HOST}:{PORT}...")

        while True:
            # Wait for an incoming client connection
            conn, addr = server_socket.accept()

            # Use a context manager to ensure the client connection closes cleanly
            with conn:
                print(f"Connected successfully to client: {addr}")

                while True:
                    # I AM PROTOCOL
                    data = conn.recv(1024)
                    if data == b'':
                        break


                    print(data)
                    message = data.decode()
                    type = int(message[:1])
                    payload = message[1:]
                    queue.put({'type': type, 'data': payload, 'ip': addr})


def response_to_dms():
    while True:
        item = queue.get()

        print(item, "is online")
        if send_to_client(item['type'], whoami, item['ip']):
            queue.task_done()


def send_to_client(type, payload, ip):
    # Define the server's IP address and port to connect to
    server_host = ip[0]  # 'localhost' for testing on the same machine
    server_port = 65432         # Must match the server's listening port

    # 1. Create a socket object
    # socket.AF_INET specifies IPv4, socket.SOCK_STREAM specifies TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            # 2. Connect to the server
            client_socket.connect((server_host, server_port))
            print(f"Connected successfully to {server_host}:{server_port}")

            # 3. Send data (Strings must be encoded to bytes)
            client_socket.sendall((str(type) + str(payload)).encode('utf-8'))
            print(f"Sent: {payload}")

        except ConnectionRefusedError:
            print(f"Failed to connect. Is the server running on port {server_port}?")
            return False
        except Exception as e:
            print(f"An error occurred: {e}")

    return True


#setup_server()

server = Thread(target=setup_server)
client = Thread(target=response_to_dms)

server.start()
client.start()

server.join()
client.join()
