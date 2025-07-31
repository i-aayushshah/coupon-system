import secrets
import base64

def generate_jwt_secret_key(length=64, use_base64=True):
    """
    Generates a secure random JWT secret key.

    Args:
        length (int): Number of bytes (not characters) to generate. Default is 64.
        use_base64 (bool): Whether to return the key as a base64-encoded string.

    Returns:
        str: The secret key as a string.
    """
    key = secrets.token_bytes(length)
    return base64.urlsafe_b64encode(key).decode() if use_base64 else key.hex()

if __name__ == "__main__":
    secret_key = generate_jwt_secret_key()
    print(f"Your JWT Secret Key:\n{secret_key}")
