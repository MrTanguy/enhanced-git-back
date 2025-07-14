import os
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from services.db.base import Base


class DB:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DB, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            load_dotenv()
            self._initialized = True
            self.host = os.getenv("BDD_HOST")
            self.database = os.getenv("BDD_NAME")
            self.user = os.getenv("BDD_USER")
            self.password = os.getenv("BDD_PSWD")
            
            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            self.connection_string = f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}/{self.database}"
            self.engine = create_engine(self.connection_string)
            self.Session = sessionmaker(bind=self.engine)

    def get_connection(self):
        """Retourne une nouvelle session SQLAlchemy."""
        return self.Session()

    def close_connection(self):
        self.Session().close()
    