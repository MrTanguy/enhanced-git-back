import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
import requests
from services.oauth.github import Github


@pytest.fixture
def github_instance():
    return Github()


@patch("services.oauth.github.requests.post")
def test_getAccessToken_success(mock_post, github_instance):
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "fake_token"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    token = github_instance.getAccessToken("fake_code")
    assert token == "fake_token"
    mock_post.assert_called_once()


@patch("services.oauth.github.requests.post")
def test_getAccessToken_failure_raises_http_exception(mock_post, github_instance):
    mock_post.side_effect = requests.exceptions.RequestException("Network error")
    with pytest.raises(HTTPException):
        github_instance.getAccessToken("fake_code")


@patch("services.oauth.github.requests.get")
def test_getUserInfo_success(mock_get, github_instance):
    mock_response = MagicMock()
    mock_response.json.return_value = {"login": "testuser", "id": 123}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    user_info = github_instance.getUserInfo("fake_token")
    assert user_info["login"] == "testuser"
    mock_get.assert_called_once()


@patch("services.oauth.github.requests.get")
def test_getUserInfo_failure_raises_http_exception(mock_get, github_instance):
    mock_get.side_effect = requests.exceptions.RequestException("Network error")
    with pytest.raises(HTTPException):
        github_instance.getUserInfo("fake_token")


@patch("services.oauth.github.requests.get")
def test_getAllPublicProjects_success(mock_get, github_instance):
    # Mock de la réponse pour user info
    mock_user_response = MagicMock()
    mock_user_response.json.return_value = {"login": "testuser"}
    mock_user_response.raise_for_status.return_value = None

    # Mock de la réponse pour les repos
    mock_repos_response = MagicMock()
    mock_repos_response.json.return_value = [
        {"id": 1, "name": "repo1", "language": "Python"},
        {"id": 2, "name": "repo2", "language": "JavaScript"},
    ]
    mock_repos_response.raise_for_status.return_value = None

    # Le side_effect permet de retourner successivement les 2 mocks
    mock_get.side_effect = [mock_user_response, mock_repos_response]

    projects = github_instance.getAllPublicProjects(123)
    assert len(projects) == 2
    assert projects[0]["language"] == "Python"
    assert projects[0]["website"] == "github"
    mock_get.assert_called()

@patch("services.oauth.github.requests.get")
def test_getAllPublicProjects_api_failure_raises_http_exception(mock_get, github_instance):
    mock_get.side_effect = requests.exceptions.RequestException("GitHub API failure")
    with pytest.raises(HTTPException):
        github_instance.getAllPublicProjects("testuser")

@patch("services.oauth.github.requests.get")
def test_getAllPublicProjects_username_not_found_raises_http_exception(mock_get, github_instance):
    # Mock de la réponse user info avec un dict vide (pas de login)
    mock_user_response = MagicMock()
    mock_user_response.json.return_value = {}
    mock_user_response.raise_for_status.return_value = None

    mock_get.return_value = mock_user_response

    with pytest.raises(HTTPException) as exc_info:
        github_instance.getAllPublicProjects(123)
    assert exc_info.value.status_code == 404


@patch("services.oauth.github.requests.get")
def test_getAllPublicProjects_user_api_failure_raises_http_exception(mock_get, github_instance):
    # Exception à la requête user info
    mock_get.side_effect = requests.exceptions.RequestException("GitHub API failure")

    with pytest.raises(HTTPException) as exc_info:
        github_instance.getAllPublicProjects(123)
    assert exc_info.value.status_code == 502


@patch("services.oauth.github.requests.get")
def test_getAllPublicProjects_repos_api_failure_raises_http_exception(mock_get, github_instance):
    # Mock user info valide
    mock_user_response = MagicMock()
    mock_user_response.json.return_value = {"login": "testuser"}
    mock_user_response.raise_for_status.return_value = None

    # Fonction side_effect qui différencie les 2 appels
    def side_effect(url, headers):
        if f"/user/" in url:
            return mock_user_response
        else:
            # Simule une exception lors de la récupération des repos
            raise requests.exceptions.RequestException("Repos API failure")

    mock_get.side_effect = side_effect

    with pytest.raises(HTTPException) as exc_info:
        github_instance.getAllPublicProjects(123)
    assert exc_info.value.status_code == 502


def test_getOauthUrl_returns_correct_url(github_instance):
    expected_url = github_instance.url_oauth
    assert github_instance.getOauthUrl() == expected_url
