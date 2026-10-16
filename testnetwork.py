import socket
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
import os

# key = os.urandom(32)
# iv = os.urandom(16)
# cipher = Cipher(algorithms.AES(key), modes.CTR(iv))

# encryptor = cipher.encryptor()
# ct = encryptor.update(b"secret") + encryptor.finalize()

# decryptor = cipher.decryptor()
# dt = decryptor.update(ct) + decryptor.finalize()

# print(ct, dt.decode())


#HANDSHAKE PROTOCOL
fernet_key = Fernet.generate_key()
_fernet = Fernet(fernet_key)

rsa_private = generate_private_key(65537, 2048)
rsa_public = rsa_private.public_key()

encrypted_key = rsa_public.encrypt(
    fernet_key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

SERVER_HOST = "10.0.0.1"
DEFAULT_SERVER_PORT = 65432

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

#     # Allow immediate reuse of the port after stopping the server (prevents "Address already in use" errors)
#     server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#     # Bind the socket to the host and port
#     server_socket.bind((SERVER_HOST, DEFAULT_SERVER_PORT))

#     # Enable the server to accept connections
#     server_socket.listen()
#     print(f"Server is listening on {SERVER_HOST}:{DEFAULT_SERVER_PORT}...")

#     server_socket.settimeout(1.0)
#     while True:
#         # Wait for an incoming client connection
#         try:
#             conn, addr = server_socket.accept()
#             conn.settimeout(1.0)
#         except TimeoutError:
#             continue

#         # Use a context manager to ensure the client connection closes cleanly
#         with conn:
#             #print(f"Connected successfully to client: {addr}")

#             while True:
#                 # GET RESPONSES FROM PEOPLE
#                 data = conn.recv(1024)
#                 if data == b'':
#                     break


#                 print("Recieved", data)


#Sends string payload to host address
def transmit_payload(info: bytes, host):
    # Define the server's IP address and port to connect to
    server_host = host  # 'localhost' for testing on the same machine

    # 1. Create a socket object
    # socket.AF_INET specifies IPv4, socket.SOCK_STREAM specifies TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            # 2. Connect to the server
            #print(f"Connected successfully to {server_host}:{DEFAULT_SERVER_PORT}")

            # 4. Receive data from the server
            # 1024 is the buffer size (max bytes to receive at once)
            client_socket.connect((server_host, DEFAULT_SERVER_PORT))
            #print(f"Connected successfully to {server_host}:{DEFAULT_SERVER_PORT}")

            # 4. Receive data from the server
            # 1024 is the buffer size (max bytes to receive at once)
            client_socket.sendall(info)

        except ConnectionRefusedError:
            return False


    return True


transmit_payload(encrypted_key, "0.0.0.0")
