import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
import requests
from services.oauth.github import Github


@pytest.fixture
def github_instance():
    return Github()


@patch("services.oauth.github.requests.post")
def test_get_access_token_success(mock_post, github_instance):
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "fake_token", "scope": "read:user"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    token = github_instance.get_access_token("fake_code")
    assert token == "fake_token"
    mock_post.assert_called_once()


@patch("services.oauth.github.requests.post")
def test_get_access_token_failure_raises_http_exception(mock_post, github_instance):
    mock_post.side_effect = requests.exceptions.RequestException("Network error")
    with pytest.raises(HTTPException):
        github_instance.get_access_token("fake_code")


@patch("services.oauth.github.requests.get")
def test_get_user_info_success(mock_get, github_instance):
    mock_response = MagicMock()
    mock_response.json.return_value = {"login": "testuser", "id": 123}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    user_info = github_instance.get_user_info("fake_token")
    assert user_info["login"] == "testuser"
    mock_get.assert_called_once()


@patch("services.oauth.github.requests.get")
def test_get_user_info_failure_raises_http_exception(mock_get, github_instance):
    mock_get.side_effect = requests.exceptions.RequestException("Network error")
    with pytest.raises(HTTPException):
        github_instance.get_user_info("fake_token")


@patch("services.oauth.github.requests.get")
def test_get_all_public_projects_success(mock_get, github_instance):
    
    mock_user_response = MagicMock()
    mock_user_response.json.return_value = {"login": "testuser"}
    mock_user_response.raise_for_status.return_value = None

    
    mock_repos_response = MagicMock()
    mock_repos_response.json.return_value = [
        {"id": 1, "name": "repo1", "language": "Python"},
        {"id": 2, "name": "repo2", "language": "JavaScript"},
    ]
    mock_repos_response.raise_for_status.return_value = None

    
    mock_get.side_effect = [mock_user_response, mock_repos_response]

    projects = github_instance.get_all_public_projects(123)
    assert len(projects) == 2
    assert projects[0]["language"] == "Python"
    assert projects[0]["website"] == "github"
    mock_get.assert_called()

@patch("services.oauth.github.requests.get")
def test_get_all_public_projects_api_failure_raises_http_exception(mock_get, github_instance):
    mock_get.side_effect = requests.exceptions.RequestException("GitHub API failure")
    with pytest.raises(HTTPException):
        github_instance.get_all_public_projects("testuser")

@patch("services.oauth.github.requests.get")
def test_get_all_public_projects_username_not_found_raises_http_exception(mock_get, github_instance):
    
    mock_user_response = MagicMock()
    mock_user_response.json.return_value = {}
    mock_user_response.raise_for_status.return_value = None

    mock_get.return_value = mock_user_response

    with pytest.raises(HTTPException) as exc_info:
        github_instance.get_all_public_projects(123)
    assert exc_info.value.status_code == 404


@patch("services.oauth.github.requests.get")
def test_get_all_public_projects_user_api_failure_raises_http_exception(mock_get, github_instance):
    
    mock_get.side_effect = requests.exceptions.RequestException("GitHub API failure")

    with pytest.raises(HTTPException) as exc_info:
        github_instance.get_all_public_projects(123)
    assert exc_info.value.status_code == 502


@patch("services.oauth.github.requests.get")
def test_get_all_public_projects_repos_api_failure_raises_http_exception(mock_get, github_instance):
    
    mock_user_response = MagicMock()
    mock_user_response.json.return_value = {"login": "testuser"}
    mock_user_response.raise_for_status.return_value = None

    
    def side_effect(url, headers):
        if f"/user/" in url:
            return mock_user_response
        else:
            raise requests.exceptions.RequestException("Repos API failure")

    mock_get.side_effect = side_effect

    with pytest.raises(HTTPException) as exc_info:
        github_instance.get_all_public_projects(123)
    assert exc_info.value.status_code == 502


def test_get_oauth_url_returns_correct_url(github_instance):
    expected_url = github_instance.url_oauth
    assert github_instance.get_oauth_url() == expected_url
