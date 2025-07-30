import os
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


class DB:
    """
    Singleton class responsible for initializing and providing
    database connections and password hashing context.

    This class ensures that only one instance handles the database connection
    and password hashing setup throughout the application lifecycle.
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DB, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not DB._initialized:
            load_dotenv()

            # Group DB config parameters in a single dict to reduce instance attrs
            self.config = {
                "user": os.getenv("BDD_USER"),
                "password": os.getenv("BDD_PSWD"),
                "host": os.getenv("BDD_HOST"),
                "port": os.getenv("BDD_PORT"),
                "database": os.getenv("BDD_NAME"),
            }

            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

            self.connection_string = (
                f"postgresql+psycopg2://{self.config['user']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
            )

            self.engine = create_engine(self.connection_string)
            self.session_factory = sessionmaker(bind=self.engine)

            DB._initialized = True

    def get_connection(self):
        """
        Return a new SQLAlchemy session.

        Use this to interact with the database in a transactional scope.
        """
        return self.session_factory()

    def close_connection(self):
        """
        Close the current SQLAlchemy session.

        Note: This closes a new session instance, so it's recommended
        to close sessions individually after use.
        """
        self.session_factory().close()
