import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
import requests
from models.connection import Connection
from services.oauth.gitlab import Gitlab


@pytest.fixture
def gitlab_instance():
    return Gitlab()


# ---------- get_access_token ----------
@patch("services.oauth.gitlab.requests.post")
def test_get_access_token_success(mock_post, gitlab_instance):
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "fake_token", "scope": "read_user"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    token = gitlab_instance.get_access_token("fake_code")
    assert token["access_token"] == "fake_token"
    mock_post.assert_called_once()


@patch("services.oauth.gitlab.requests.post")
def test_get_access_token_invalid_scope_raises_exception(mock_post, gitlab_instance):
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "fake_token", "scope": "invalid"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    with pytest.raises(HTTPException):
        gitlab_instance.get_access_token("fake_code")


@patch("services.oauth.gitlab.requests.post")
def test_get_access_token_failure(mock_post, gitlab_instance):
    mock_post.side_effect = requests.exceptions.RequestException("Network error")
    with pytest.raises(HTTPException):
        gitlab_instance.get_access_token("fake_code")


# ---------- get_user_info ----------
@patch("services.oauth.gitlab.requests.get")
@patch("services.oauth.gitlab.Data.decrypt", return_value="fake_token")
def test_get_user_info_success(mock_decrypt, mock_get, gitlab_instance):
    mock_response = MagicMock()
    mock_response.json.return_value = {"username": "testuser", "id": 123}
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    fake_connection = Connection()
    fake_connection.access_token = "fake_token"

    user_info = gitlab_instance.get_user_info(fake_connection)
    assert user_info["username"] == "testuser"
    mock_get.assert_called_once()
    mock_decrypt.assert_called_once_with("fake_token")


@patch("services.oauth.gitlab.requests.get")
@patch("services.oauth.gitlab.Data.decrypt", return_value="fake_token")
def test_get_user_info_unauthorized_triggers_refresh(mock_decrypt, mock_get, gitlab_instance):
    fake_connection = Connection()
    fake_connection.access_token = "fake_token"
    fake_connection.refresh_token = "refresh_token"

    mock_unauthorized = MagicMock()
    mock_unauthorized.status_code = 401
    mock_unauthorized.raise_for_status.side_effect = requests.exceptions.HTTPError()

    mock_success = MagicMock()
    mock_success.status_code = 200
    mock_success.json.return_value = {"username": "refreshed_user"}

    # Le premier appel renvoie 401, le deuxième marche
    mock_get.side_effect = [mock_unauthorized, mock_success]

    with patch.object(gitlab_instance, "refresh_gitlab_token", return_value="new_token") as mock_refresh:
        result = gitlab_instance.get_user_info(fake_connection)
        assert result["username"] == "refreshed_user"
        mock_refresh.assert_called_once()


@patch("services.oauth.gitlab.requests.get")
@patch("services.oauth.gitlab.Data.decrypt", return_value="fake_token")
def test_get_user_info_failure(mock_decrypt, mock_get, gitlab_instance):
    mock_get.side_effect = requests.exceptions.RequestException("Network error")
    fake_connection = Connection()
    fake_connection.access_token = "fake_token"
    with pytest.raises(HTTPException):
        gitlab_instance.get_user_info(fake_connection)


# ---------- get_all_public_projects ----------
@patch("services.oauth.gitlab.requests.get")
def test_get_all_public_projects_success(mock_get, gitlab_instance):
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"id": 1, "name": "repo1", "language": "Python", "web_url": "https://gitlab.com/repo1"},
        {"id": 2, "name": "repo2", "language": "JavaScript", "web_url": "https://gitlab.com/repo2"},
    ]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    projects = gitlab_instance.get_all_public_projects("123")
    assert len(projects) == 2
    assert projects[0]["website"] == "gitlab"


@patch("services.oauth.gitlab.requests.get")
def test_get_all_public_projects_failure(mock_get, gitlab_instance):
    mock_get.side_effect = requests.exceptions.RequestException("API failure")
    with pytest.raises(HTTPException):
        gitlab_instance.get_all_public_projects("123")


# ---------- get_oauth_url ----------
def test_get_oauth_url_returns_correct_url(gitlab_instance):
    expected_url = gitlab_instance.url_oauth
    assert gitlab_instance.get_oauth_url() == expected_url
