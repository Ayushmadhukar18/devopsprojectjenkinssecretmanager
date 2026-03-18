import os
import base64
from cryptography.fernet import Fernet

def _get_key() -> bytes:
    """Load or generate the encryption key."""
    key = os.environ.get("ENCRYPTION_KEY")
    if key:
        return key.encode()
    # Fallback for development — in production always set ENCRYPTION_KEY
    key_file = os.path.join(os.path.dirname(__file__), ".secret.key")
    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            return f.read()
    new_key = Fernet.generate_key()
    with open(key_file, "wb") as f:
        f.write(new_key)
    return new_key

_fernet = Fernet(_get_key())

def encrypt_value(plaintext: str) -> str:
    """Encrypt a string and return a base64 token."""
    return _fernet.encrypt(plaintext.encode()).decode()

def decrypt_value(token: str) -> str:
    """Decrypt a base64 token and return the original string."""
    return _fernet.decrypt(token.encode()).decode()
