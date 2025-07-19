import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from models.user import User
from repositories.UserRepository import UserRepository


@pytest.fixture
def mock_user():
    return User(id=1, username="existing@example.com", password="hashedpass", is_active=True)


@pytest.fixture
def mock_db_session_with_user(mock_user):
    mock_session = MagicMock()
    mock_session.execute.return_value.scalar_one_or_none.return_value = mock_user
    return mock_session


@pytest.fixture
def mock_db_session_no_user():
    mock_session = MagicMock()
    mock_session.execute.return_value.scalar_one_or_none.return_value = None
    return mock_session


@pytest.fixture
def user_repo_with_user(mock_db_session_with_user):
    with patch("repositories.UserRepository.DB") as MockedDB:
        db_instance = MockedDB.return_value
        db_instance.get_connection.return_value.__enter__.return_value = mock_db_session_with_user
        db_instance.pwd_context.hash.return_value = "hashedpass"
        db_instance.pwd_context.verify.return_value = True
        return UserRepository()


@pytest.fixture
def user_repo_without_user(mock_db_session_no_user):
    with patch("repositories.UserRepository.DB") as MockedDB:
        db_instance = MockedDB.return_value
        db_instance.get_connection.return_value.__enter__.return_value = mock_db_session_no_user
        db_instance.pwd_context.verify.return_value = False
        return UserRepository()


def test_create_user_success():
    mock_session = MagicMock()
    mock_session.execute.return_value.scalar_one_or_none.return_value = None  # Pas de conflit

    with patch("repositories.UserRepository.DB") as MockedDB:
        db_instance = MockedDB.return_value
        db_instance.get_connection.return_value.__enter__.return_value = mock_session
        db_instance.pwd_context.hash.return_value = "hashedpass"

        repo = UserRepository()
        user = repo.create("new@example.com", "plainpass")

        assert user.username == "new@example.com"
        assert user.password == "hashedpass"
        mock_session.add.assert_called()
        mock_session.commit.assert_called()


def test_create_user_conflict(mock_db_session_with_user):
    mock_db_session_with_user.commit.side_effect = IntegrityError("conflict", {}, None)
    with patch("repositories.UserRepository.DB") as MockedDB:
        db_instance = MockedDB.return_value
        db_instance.get_connection.return_value.__enter__.return_value = mock_db_session_with_user
        db_instance.pwd_context.hash.return_value = "hashedpass"

        repo = UserRepository()
        with pytest.raises(HTTPException) as exc:
            repo.create("existing@example.com", "pass")
        assert exc.value.status_code == 409


def test_read_by_id_success():
    user = User(id=1, username="existing@example.com", password="hashedpass", is_active=True)
    
    mock_session = MagicMock()
    mock_session.execute.return_value.unique.return_value.scalar_one_or_none.return_value = user

    with patch("repositories.UserRepository.DB") as MockedDB:
        db_instance = MockedDB.return_value
        db_instance.get_connection.return_value.__enter__.return_value = mock_session
        repo = UserRepository()
        result = repo.read_by_id(1)
        assert result.username == "existing@example.com"


def test_read_by_id_not_found():
    mock_session = MagicMock()
    mock_session.execute.return_value.unique.return_value.scalar_one_or_none.return_value = None

    with patch("repositories.UserRepository.DB") as MockedDB:
        db_instance = MockedDB.return_value
        db_instance.get_connection.return_value.__enter__.return_value = mock_session
        repo = UserRepository()
        with pytest.raises(HTTPException) as exc:
            repo.read_by_id(999)
        assert exc.value.status_code == 404


def test_read_by_username_success(user_repo_with_user):
    user = user_repo_with_user.read_by_username("existing@example.com")
    assert user.username == "existing@example.com"


def test_read_by_username_not_found(user_repo_without_user):
    user = user_repo_without_user.read_by_username("notfound@example.com")
    assert user is None


def test_login_success(user_repo_with_user):
    user = user_repo_with_user.login("existing@example.com", "any")
    assert user.username == "existing@example.com"


def test_login_wrong_credentials(user_repo_without_user):
    user = user_repo_without_user.login("wrong@example.com", "bad")
    assert user is None


def test_update_user_success(mock_user):
    mock_session = MagicMock()

    with patch("repositories.UserRepository.DB") as MockedDB:
        db_instance = MockedDB.return_value
        db_instance.get_connection.return_value.__enter__.return_value = mock_session
        db_instance.pwd_context.hash.return_value = "hashedpass"

        repo = UserRepository()
        repo.update(mock_user)

        assert mock_user.password == "hashedpass"
        mock_session.execute.assert_called()
        mock_session.commit.assert_called()


def test_update_user_exception(mock_user):
    mock_session = MagicMock()
    mock_session.commit.side_effect = Exception("fail")

    with patch("repositories.UserRepository.DB") as MockedDB:
        db_instance = MockedDB.return_value
        db_instance.get_connection.return_value.__enter__.return_value = mock_session
        db_instance.pwd_context.hash.return_value = "hashedpass"

        repo = UserRepository()
        with pytest.raises(HTTPException) as exc:
            repo.update(mock_user)
        assert exc.value.status_code == 500


def test_delete_user_success():
    mock_session = MagicMock()
    mock_session.execute.return_value.rowcount = 1

    with patch("repositories.UserRepository.DB") as MockedDB:
        db_instance = MockedDB.return_value
        db_instance.get_connection.return_value.__enter__.return_value = mock_session

        repo = UserRepository()
        repo.delete(1)
        mock_session.commit.assert_called()


def test_delete_user_not_found():
    mock_session = MagicMock()
    mock_session.execute.return_value.rowcount = 0

    with patch("repositories.UserRepository.DB") as MockedDB:
        db_instance = MockedDB.return_value
        db_instance.get_connection.return_value.__enter__.return_value = mock_session

        repo = UserRepository()
        with pytest.raises(HTTPException) as exc:
            repo.delete(999)
        assert exc.value.status_code == 404
