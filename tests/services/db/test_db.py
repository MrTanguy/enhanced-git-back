import os
import pytest
from unittest.mock import patch, MagicMock
from services.db.db import DB


@pytest.fixture(autouse=True)
def clear_singleton():
    """Réinitialise le singleton DB entre les tests."""
    DB._instance = None


@pytest.fixture
def mock_env():
    """Mock les variables d'environnement."""
    with patch.dict(os.environ, {
        "BDD_HOST": "localhost",
        "BDD_PORT": "5432",
        "BDD_NAME": "testdb",
        "BDD_USER": "testuser",
        "BDD_PSWD": "testpassword"
    }):
        yield


@pytest.fixture
def mock_sqlalchemy():
    """Mocke SQLAlchemy: create_engine et sessionmaker."""
    with patch("services.db.db.create_engine") as mock_create_engine, \
         patch("services.db.db.sessionmaker") as mock_sessionmaker:

        # Mock l'engine SQLAlchemy
        mock_engine = MagicMock(name="MockEngine")
        mock_create_engine.return_value = mock_engine

        # Mock le sessionmaker
        mock_session_instance = MagicMock(name="SessionInstance")
        mock_sessionmaker_callable = MagicMock(return_value=mock_session_instance)
        mock_sessionmaker.return_value = mock_sessionmaker_callable

        yield {
            "engine": mock_engine,
            "sessionmaker": mock_sessionmaker,
            "session_callable": mock_sessionmaker_callable,
            "session_instance": mock_session_instance,
        }

def test_db_initialization(mock_env, mock_sqlalchemy):
    db_instance = DB()

    # Vérifie que la chaîne de connexion est correcte
    expected_conn_str = "postgresql+psycopg2://testuser:testpassword@localhost:5432/testdb"
    assert db_instance.connection_string == expected_conn_str

    # Vérifie les mocks appelés
    mock_sqlalchemy["sessionmaker"].assert_called_once_with(bind=mock_sqlalchemy["engine"])
    assert db_instance.engine == mock_sqlalchemy["engine"]
    session = db_instance.get_connection()
    assert session == mock_sqlalchemy["session_instance"]



def test_db_get_connection_returns_session(mock_env, mock_sqlalchemy):
    db_instance = DB()
    session = db_instance.get_connection()

    # Vérifie que get_connection retourne bien la session mockée
    assert session == mock_sqlalchemy["session_instance"]
    mock_sqlalchemy["session_callable"].assert_called_once()


def test_db_is_singleton(mock_env, mock_sqlalchemy):
    db1 = DB()
    db2 = DB()
    assert db1 is db2 

def test_db_close_connection_closes_session(mock_env, mock_sqlalchemy):
    db_instance = DB()

    # Appelle la méthode à tester
    db_instance.close_connection()

    # Vérifie que la méthode close a bien été appelée sur la session
    mock_sqlalchemy["session_callable"]().close.assert_called_once()
