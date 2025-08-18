
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet


class Data:
    """Use to encrypt/decrypt data for the database"""

    def __init__(self):
        load_dotenv()
        key = os.getenv('ENCRYPT_DATA').encode()
        self.cipher_suite = Fernet(key=key)

    def encrypt(self, data: bytes):
        """Use to encrypt data for the database"""
        if data:
            return self.cipher_suite.encrypt(data.encode()).decode()
        return None

    def decrypt(self, data: str) -> str:
        """Use to encrypt data for the database"""
        if data:
            return self.cipher_suite.decrypt(data.encode()).decode()
        return None
