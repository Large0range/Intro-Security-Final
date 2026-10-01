import bcrypt


def hash_password(plain_password):
    # Convert string password to bytes
    password_bytes = plain_password.encode('utf-8')

    # Generate a secure salt (automatically generates a cryptographically secure salt)
    salt = bcrypt.gensalt()

    # Hash the password
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password


def verify_password(plain_password, stored_hash):
    password_bytes = plain_password.encode('utf-8')

    # Check if the password matches the hash
    return bcrypt.checkpw(password_bytes, stored_hash)
