import base64
from functools import wraps

import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from Crypto.Hash import SHA3_512
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes

from Crypto.Signature import pkcs1_15



_fernet = None
_kdf = None

def requires_fernet(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if _fernet is None:
            raise RuntimeError("Fernet not initialized")
        return func(*args, **kwargs)
    return wrapper


def hash_password(plain_password):
    # Convert string password to bytes
    password_bytes = plain_password.encode('utf-8')



    bcrypt_salt = bcrypt.gensalt()
    # Hash the password
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt_salt)
    return hashed_password


def verify_password(plain_password, stored_hash):
    password_bytes = plain_password.encode('utf-8')

    # Check if the password matches the hash
    return bcrypt.checkpw(password_bytes, stored_hash)

def init_crypt(password_bytes, salt):
    global _fernet, _kdf

    _kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=2_000_000
    )


    _fernet = Fernet(base64.urlsafe_b64encode(_kdf.derive(password_bytes)))

@requires_fernet
def encrypt_fernet(message):
    return _fernet.encrypt(message.encode())

@requires_fernet
def decrypt_fernet(message):
    return _fernet.decrypt(message)




######################
# NETWORK SECURITY FUNCTIONS
# USED FOR TUNNELING AUTHENTICATION SIGNATURES
# NOT USED FOR BASE LOCAL MACHINE ENCRYPTION
# ####################


from Crypto.Hash import SHA3_512
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
import os

from Crypto.Signature import pkcs1_15

RSA_KEY_FILE = "rsa.pem"

#####################################
# Grabs the RSA public and private keys from file
# Returns:
#   public key      - bytes
#   private key     - bytes
#####################################
def read_keys_from_file() -> tuple[bytes, bytes]:
    with open(RSA_KEY_FILE, "rb") as file:
        priv_key = RSA.import_key(file.read())
        pub_key = priv_key.public_key()

    return priv_key.export_key(), pub_key.export_key()


#####################################
# Generates the RSA public and private keys
# Returns:
#   public key      - bytes
#   private key     - bytes
#####################################
def generate_rsa_keys() -> tuple[bytes, bytes]:
    priv_key = RSA.generate(4096)
    pub_key = priv_key.public_key()

    with open(RSA_KEY_FILE, "wb") as file:
        file.write(priv_key.export_key())

    return priv_key.export_key(), pub_key.export_key()


#########################################################
# Takes a rsa_public_key      - bytes
# Takes a message to encrypt -  bytes  - used later for signing
# Returns:
#   encrypted session key - 512 bytes
#   nonce                 - 16 bytes
#   tag                   - 16 bytes
#   ciphertext            - Unknown bytes
#########################################################
def encrypt_generate_aes_secrets(rsa_pub_key: bytes, data: bytes) -> tuple[bytes, bytes, bytes, bytes, bytes]:
    session_key = get_random_bytes(16)

    # Encrypt the session key with the public RSA key

    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(rsa_pub_key), SHA3_512)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt the data with the AES session key

    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)

    return enc_session_key, cipher_aes.nonce, tag, ciphertext, session_key



#######################################################
# Decrypts the AES key from the encrypted key
# Sets up the AES Cipher and decrypts handshake message
# Takes:
#   RSA Private Key         - bytes
#   Encrypted Session Key   - bytes
#   Nonce                   - bytes
#   Mac Tag                 - bytes
#   Cipher Text             - bytes
# Returns:
#   Plain Text              - bytes
#   AES Key                 - bytes
# --- Empty bytes on decrypt failure
#######################################################
def decrypt_aes_secrets_verify(rsa_priv_key: bytes, enc_session_key: bytes, nonce: bytes, tag: bytes, ciphertext: bytes) -> tuple[bytes, bytes]:
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(rsa_priv_key), SHA3_512)

    aes_key = cipher_rsa.decrypt(enc_session_key)

    cipher_aes = AES.new(aes_key, AES.MODE_EAX, nonce)
    try:
        plaintext = cipher_aes.decrypt_and_verify(ciphertext, tag)
        return plaintext, aes_key
    except ValueError:
        return b"", b""




######################################################
# Signs and hashes message with the RSA private key
# Takes an RSA private key  - bytes
# Takes message to sign     - bytes
# Returns:
#   Hash of the message     - bytes
#   Signature               - bytes
######################################################
def sign_message(priv_key, data) -> tuple[bytes, bytes]:
    key = RSA.import_key(priv_key)

    h = SHA3_512.new(data)
    signature = pkcs1_15.new(key).sign(h)

    return h.digest(), signature




#######################################################
# Verfies the signature of a hashed message
# Takes an RSA public key   - bytes
# Takes original message    - bytes
# Takes obtained hash       - bytes
# Takes signature of hash   - bytes
# Returns
#   - True  if signature is valid
#   - False if not
#######################################################
def verify_signature(pub_key: bytes, message: bytes, signature: bytes) -> bool:
    key = RSA.import_key(pub_key)

    h = SHA3_512.new(message)

    try:
        pkcs1_15.new(key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False


#####################################################
# Encrypts data with AES session key
# Takes AES Session Key         - bytes
# Takes data                    - bytes
# Returns:
#   Byte String - Nonce      +Tag      +CipherText
#                 16 Bytes    16 Bytes  Rem Bytes
#####################################################
def encrypt_aes(session_key: bytes, data: bytes) -> bytes:
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)

    return cipher_aes.nonce + tag + ciphertext



#####################################################
# Decrypts data with AES session key
# Takes AES Session Key         - bytes
# Takes data                    - bytes
# Returns:
#   Plain Text                  - bytes
# --- Empty bytes on decrypt failure
#####################################################
def decrypt_aes(session_key: bytes, data: bytes) -> bytes:
    nonce = data[:16]
    tag = data[16:32]
    ciphertext = data[32:]

    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)

    try:
        return cipher_aes.decrypt_and_verify(ciphertext, tag)
    except ValueError:
        return b""


# CODE EXAMPLE
# FULL HANDSHAKE BETWEEN MACHINES
#
# Assume passing of data between machines
#
# Machine 1 - M1:
# Machine 2 - M2:

# M1: Generate public and private keys for handshake
#: priv, pub = generate_rsa_keys()

# M2: Receive public key and pass message to AES encrypt and send back -- should be standardized for handshakes
# M2: Generate encrypted session key, nonce, mac tag, and cipher text
#: session_key, nonce, tag, cipher_text = encrypt_generate_aes_secrets(pub, b"I am Boh Mingle")

# M1: Receive encrypted aes key, nonce, mac tag, and cipher text
# M1: Generate plain text of the AES encrypted message, verifies that tunnel can talk properly
#: plain_text, aes_key = decrypt_aes_secrets_verify(priv, session_key, nonce, tag, cipher_text)

# M1: Sign Message with decrypted plain text            -- should be used as M2 knows sent message
# M1: Generate hash and signature for hash
#: hash, signature = sign_message(priv, plain_text)

# M2: Receive hash and signature
# M2: Verify hash and signature against previously sent message
#:if verify_signature(pub, b"I am Boh Mingle", hash, signature):
#:    print("Signature Valid -- Person Fully Authed")
#: else:
#:     print("Signature Invalid -- Person Not Authed")


# CODE EXAMPLE
# AES ENCRYPTION

# Encrypt byte message with AES key
#   -- Used from previous code example for uncommenting purposes
#   -- Should never have to call this function without handshake creating a key
#: data = encrypt_aes(aes_key, b"Hello Boh Mingle")

# Decrypt byte message with AES key
#   -- See comments above, same logic
#: plain_text = decrypt_aes(aes_key, data)
