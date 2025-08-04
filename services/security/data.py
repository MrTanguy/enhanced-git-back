
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet


class Data:

    def __init__(self):
        load_dotenv()
        key = os.getenv('ENCRYPT_DATA').encode()
        self.cipher_suite = Fernet(key=key)

    def encrypt(self, data: bytes):
        if data:
            return self.cipher_suite.encrypt(data.encode()).decode()

    def decrypt(self, data: str) -> str:
        if data:
            return self.cipher_suite.decrypt(data.encode()).decode()