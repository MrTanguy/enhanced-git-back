import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status, HTTPException
from main import app
from services.security.bearer import Bearer

client = TestClient(app)

VALID_BEARER_TOKEN = "valid_token"
VALID_USER_ID = 123

@pytest.fixture
def mock_bearer_verify():
    with patch.object(Bearer, "verify") as mock_verify:
        def side_effect(token):
            if token != VALID_BEARER_TOKEN:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            return {"id": VALID_USER_ID}
        mock_verify.side_effect = side_effect
        yield mock_verify

@pytest.fixture
def mock_github_service():
    # Patch init_website_service to return a mock with get_user_info method
    with patch("routers.user.init_website_service") as mock_init_service:
        mock_service = MagicMock()
        mock_service.get_user_info.return_value = {"login": "mocked_username"}
        mock_init_service.return_value = mock_service
        yield mock_init_service

def make_mock_user(connections=None, portfolios=None):
    mock_user = MagicMock()
    mock_user.connections = connections or []
    mock_user.portfolios = portfolios or []
    return mock_user

@pytest.fixture
def mock_get_user_data():
    # Provide a default mock user with one connection and one portfolio
    mock_connection = MagicMock()
    mock_connection.website = "github"
    mock_connection.account_id = 111
    mock_connection.access_token = "mocked_token"

    mock_portfolio = MagicMock()
    mock_portfolio.uuid = "uuid123"
    mock_portfolio.title = "My Portfolio"
    mock_portfolio.content = ["content1", "content2"]

    user_mock = make_mock_user(
        connections=[mock_connection],
        portfolios=[mock_portfolio]
    )
    with patch("repositories.user_repository.UserRepository.read_by_id", return_value=user_mock):
        yield

def test_get_user_data_default_all(mock_bearer_verify, mock_get_user_data, mock_github_service):
    headers = {"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    response = client.get("/user/data", headers=headers)

    assert response.status_code == 200
    json_data = response.json()

    assert "connections" in json_data
    assert "portfolios" in json_data

    assert json_data["connections"][0]["website"] == "github"
    assert json_data["connections"][0]["username"] == "mocked_username"
    assert json_data["connections"][0]["id"] == 111

    assert json_data["portfolios"][0]["uuid"] == "uuid123"
    assert json_data["portfolios"][0]["title"] == "My Portfolio"

def test_get_user_data_only_connections(mock_bearer_verify, mock_github_service):
    mock_connection = MagicMock()
    mock_connection.website = "github"
    mock_connection.account_id = 111
    mock_connection.access_token = "mocked_token"

    user_mock = make_mock_user(connections=[mock_connection], portfolios=[])
    with patch("repositories.user_repository.UserRepository.read_by_id", return_value=user_mock):
        headers = {"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
        response = client.get("/user/data?types=connections", headers=headers)

        assert response.status_code == 200
        json_data = response.json()
        assert "connections" in json_data
        assert "portfolios" not in json_data

def test_get_user_data_only_portfolios(mock_bearer_verify):
    mock_portfolio = MagicMock()
    mock_portfolio.uuid = "uuid123"
    mock_portfolio.title = "My Portfolio"
    mock_portfolio.content = ["content1", "content2"]

    user_mock = make_mock_user(connections=[], portfolios=[mock_portfolio])
    with patch("repositories.user_repository.UserRepository.read_by_id", return_value=user_mock):
        headers = {"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
        response = client.get("/user/data?types=portfolios", headers=headers)

        assert response.status_code == 200
        json_data = response.json()
        assert "connections" not in json_data
        assert "portfolios" in json_data

def test_get_user_data_invalid_type(mock_bearer_verify):
    headers = {"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    response = client.get("/user/data?types=invalidtype", headers=headers)

    assert response.status_code == 400
    assert response.json()["detail"] == "Unknown type: invalidtype"

def test_get_user_data_internal_error(mock_bearer_verify):
    with patch("repositories.user_repository.UserRepository.read_by_id") as mock_read_by_id:
        mock_read_by_id.side_effect = Exception("Unexpected error")

        headers = {"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
        response = client.get("/user/data", headers=headers)

        assert response.status_code == 500
        assert response.json()["detail"] == "An error occurred"
