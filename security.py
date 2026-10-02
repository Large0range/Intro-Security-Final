import base64
import os
from functools import wraps

import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


_fernet = None
_kdf = None
key = ""

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
