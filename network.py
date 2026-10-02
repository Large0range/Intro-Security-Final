import socket


DEFAULT_SERVER_PORT = 65432

def send_friend_request(name, email):
    connect_to_friend(name, email)
    if get_friend_response(name, email):
        print("Accepted")



#Fake Friend Protocol
def connect_to_friend(name, email):
    run_client(host="0.0.0.0", port=DEFAULT_SERVER_PORT, name=name, email=email)

def get_friend_response(name, email):
    return True



def run_client(host, port, name, email):
    # Define the server's IP address and port to connect to
    server_host = host  # 'localhost' for testing on the same machine
    server_port = port         # Must match the server's listening port

    areyou = {
        "name": name,
        "email": email
    }


    # 1. Create a socket object
    # socket.AF_INET specifies IPv4, socket.SOCK_STREAM specifies TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            # 2. Connect to the server
            client_socket.connect((server_host, server_port))
            print(f"Connected successfully to {server_host}:{server_port}")


            # 3. Send data (Strings must be encoded to bytes)
            client_socket.sendall(str(areyou).encode('utf-8'))
            print(f"Sent: {areyou}")

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
