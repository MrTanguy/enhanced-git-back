import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from repositories.ConnectionRepository import ConnectionRepository
from models.user import User
from models.connection import Connection
from models.user_connection import User_Connection


@pytest.fixture
def mock_db_session(mocker):
    """Patch the DB connection and return a mocked session."""
    mocked_session = MagicMock()
    mocked_context_manager = MagicMock()
    mocked_context_manager.__enter__.return_value = mocked_session
    mocked_context_manager.__exit__.return_value = None

    mocker.patch('services.db.db.DB.get_connection', return_value=mocked_context_manager)
    return mocked_session


@pytest.fixture
def repository():
    return ConnectionRepository()


##########
# CREATE #
##########

def test_create_new_connection_and_link(repository, mock_db_session):
    """Should create a new connection and link it to the user."""

    mock_user = MagicMock()
    mock_user.connections = []
    mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [mock_user, None]  # user found, no connection

    repository.create(user_id=1, website="gitlab", access_token="abc", account_id=42, service="gitlab")

    assert mock_db_session.add.called
    assert mock_db_session.commit.call_count == 1
    assert len(mock_user.connections) == 1
    assert isinstance(mock_user.connections[0], Connection)


def test_create_existing_connection_and_link(repository, mock_db_session):
    """Should link existing connection to user if not already linked."""

    mock_user = MagicMock()
    mock_connection = MagicMock()
    mock_user.connections = []

    mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [mock_user, mock_connection, None]

    repository.create(user_id=1, website="github", access_token="xyz", account_id=99, service="github")

    assert mock_db_session.commit.called
    assert mock_connection in mock_user.connections


def test_create_connection_already_linked(repository, mock_db_session):
    """Should raise HTTPException 208 if user is already linked to connection."""

    mock_user = MagicMock()
    mock_connection = MagicMock()
    mock_jointure = MagicMock()

    mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [mock_user, mock_connection, mock_jointure]

    with pytest.raises(HTTPException) as exc:
        repository.create(user_id=1, website="gitlab", access_token="abc", account_id=42, service="gitlab")

    assert exc.value.status_code == status.HTTP_208_ALREADY_REPORTED


def test_create_connection_integrity_error(repository, mock_db_session):
    """Should raise 400 if IntegrityError is thrown."""
    mock_user = MagicMock()
    mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [mock_user, None]
    mock_db_session.commit.side_effect = IntegrityError("statement", "params", "orig")

    with pytest.raises(HTTPException) as exc:
        repository.create(user_id=1, website="gitlab", access_token="abc", account_id=42, service="gitlab")

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


########
# READ #
########

def test_read_connections_for_user(repository, mock_db_session):
    """Should return the user's connections."""
    mock_user = MagicMock()
    mock_user.connections = ["conn1", "conn2"]
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_user

    result = repository.read(user_id=1)

    assert result == ["conn1", "conn2"]


##########
# DELETE #
##########

def test_delete_existing_connection_and_jointure(repository, mock_db_session):
    """Should delete user-connection jointure and connection if no users left."""

    mock_connection = MagicMock(id=99)
    mock_jointure = MagicMock()

    mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [mock_connection, mock_jointure]
    mock_db_session.query().filter().count.return_value = 0  # no users left

    result = repository.delete(user_id=1, account_id=42)

    assert mock_db_session.delete.call_count == 2  # jointure and connection
    assert mock_db_session.commit.call_count == 2
    assert result == {"message": "Connection deleted successfully."}


def test_delete_connection_only_jointure(repository, mock_db_session):
    """Should delete only jointure if other users remain."""

    mock_connection = MagicMock(id=101)
    mock_jointure = MagicMock()

    mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [mock_connection, mock_jointure]
    mock_db_session.query().filter().count.return_value = 1  # other users exist

    result = repository.delete(user_id=1, account_id=101)

    assert mock_db_session.delete.call_count == 1  # only jointure
    assert mock_db_session.commit.call_count == 1
    assert result == {"message": "Connection deleted successfully."}


def test_delete_connection_not_found(repository, mock_db_session):
    """Should raise 404 if connection not found."""
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None

    with pytest.raises(HTTPException) as exc:
        repository.delete(user_id=1, account_id=999)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


def test_delete_jointure_not_found(repository, mock_db_session):
    """Should raise 404 if jointure not found."""

    mock_connection = MagicMock()
    mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [mock_connection, None]

    with pytest.raises(HTTPException) as exc:
        repository.delete(user_id=1, account_id=42)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND

def test_read_user_not_found(repository, mock_db_session):
    """read() returns None if user not found"""
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    result = repository.read(user_id=999)
    assert result is None


def test_delete_jointure_not_found_raises(repository, mock_db_session):
    """delete() raises 404 if jointure not found - already done but pour garantir couverture"""
    mock_connection = MagicMock()
    mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [mock_connection, None]
    with pytest.raises(HTTPException) as exc:
        repository.delete(user_id=1, account_id=42)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


def test_delete_raises_internal_error(repository, mock_db_session):
    """delete() raises 500 on unexpected exceptions"""
    mock_db_session.execute.side_effect = Exception("Unexpected error")
    with pytest.raises(HTTPException) as exc:
        repository.delete(user_id=1, account_id=42)
    assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

