import json
import socket
from threading import Thread




whoami = {
    "name": "Boh Mingle",
    "email": "root"
}

# Define host and port
# '0.0.0.0' listens on all available network interfaces (local network + localhost)
# Use '127.0.0.1' if you only want to allow connections from the same machine
HOST = "0.0.0.0"
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
        server_socket.listen(1)
        print(f"Server is listening on {HOST}:{PORT}...")

        while True:
            # Wait for an incoming client connection
            conn, addr = server_socket.accept()

            # Use a context manager to ensure the client connection closes cleanly
            with conn:
                print(f"Connected successfully to client: {addr}")

                while True:
                    # Receive data from the client (buffer size of 4096 bytes)
                    data = conn.recv(4096)

                    # If no data is received, the client has disconnected
                    if not data:
                        print(f"Client {addr} disconnected.")
                        break

                    lookingfor = convert_byte_to_json(data)
                    if lookingfor == whoami:
                        print(whoami)
                        conn.sendall("yes".encode())
                    else:
                        conn.sendall("no".encode())



def run_client():
    # Define the server's IP address and port to connect to
    server_host = '127.0.0.1'  # 'localhost' for testing on the same machine
    server_port = 65432         # Must match the server's listening port

    # 1. Create a socket object
    # socket.AF_INET specifies IPv4, socket.SOCK_STREAM specifies TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            # 2. Connect to the server
            client_socket.connect((server_host, server_port))
            print(f"Connected successfully to {server_host}:{server_port}")

            # 3. Send data (Strings must be encoded to bytes)
            message = "Hello, Server!"
            client_socket.sendall(message.encode('utf-8'))
            print(f"Sent: {message}")

            # 4. Receive data from the server
            # 1024 is the buffer size (max bytes to receive at once)
            response_bytes = client_socket.recv(1024)
            if response_bytes:
                response_message = response_bytes.decode('utf-8')
                print(f"Received from server: {response_message}")
            else:
                print("Server closed the connection.")

        except ConnectionRefusedError:
            print(f"Failed to connect. Is the server running on port {server_port}?")
        except Exception as e:
            print(f"An error occurred: {e}")


setup_server()

#server = Thread(target=setup_server)
#client = Thread(target=run_client)

#server.start()
#client.start()

#server.join()
#client.join()
