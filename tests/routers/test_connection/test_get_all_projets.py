import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from main import app
from services.security.bearer import Bearer
from repositories.ConnectionRepository import ConnectionRepository

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
def mock_init_website_service():
    with patch("routers.connection.init_website_service") as mock_init:
        mock_service = MagicMock()
        mock_service.getAllPublicProjects.return_value = [{"name": "Mock Project"}]
        mock_init.return_value = mock_service
        yield mock_init


@pytest.fixture
def mock_connection_repository():
    with patch.object(ConnectionRepository, "read") as mock_read:
        yield mock_read


def test_get_all_projects_authorized(
    mock_bearer_verify, mock_init_website_service, mock_connection_repository
):
    mock_connection = MagicMock()
    mock_connection.account_id = 123
    mock_connection.website = "github"
    mock_connection_repository.return_value = [mock_connection]

    response = client.get(
        "/connect/projects",
        params={"account_id": 123, "website": "github"},
        headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    )

    assert response.status_code == 200
    assert response.json() == [{"name": "Mock Project"}]


def test_get_all_projects_unauthorized(
    mock_bearer_verify, mock_init_website_service, mock_connection_repository
):
    mock_connection = MagicMock()
    mock_connection.account_id = 123
    mock_connection.website = "github"
    mock_connection_repository.return_value = [mock_connection]

    response = client.get(
        "/connect/projects",
        params={"account_id": 123, "website": "github"},
        headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


def test_get_all_projects_forbidden(
    mock_bearer_verify, mock_init_website_service, mock_connection_repository
):
    mock_connection = MagicMock()
    mock_connection.account_id = 999
    mock_connection.website = "gitlab"
    mock_connection_repository.return_value = [mock_connection]

    response = client.get(
        "/connect/projects",
        params={"account_id": 123, "website": "github"},
        headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "This isn't a connected account."


def test_get_all_projects_no_connections(
    mock_bearer_verify, mock_init_website_service, mock_connection_repository
):
    mock_connection_repository.return_value = []

    response = client.get(
        "/connect/projects",
        params={"account_id": 123, "website": "github"},
        headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "This isn't a connected account."


def test_init_service_called_with_correct_website(
    mock_bearer_verify, mock_init_website_service, mock_connection_repository
):
    mock_connection = MagicMock()
    mock_connection.account_id = 123
    mock_connection.website = "github"
    mock_connection_repository.return_value = [mock_connection]

    website_param = "github"
    response = client.get(
        "/connect/projects",
        params={"account_id": 123, "website": website_param},
        headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    )

    mock_init_website_service.assert_called_once_with(website=website_param)
    assert response.status_code == 200


def test_get_all_projects_init_service_error(
    mock_bearer_verify, mock_connection_repository
):
    mock_connection = MagicMock()
    mock_connection.account_id = 123
    mock_connection.website = "github"
    mock_connection_repository.return_value = [mock_connection]

    with patch(
        "routers.connection.init_website_service",
        side_effect=HTTPException(status_code=400, detail="Invalid website")
    ):
        response = client.get(
            "/connect/projects",
            params={"account_id": 123, "website": "unknown_site"},
            headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
        )

    print(response.json())

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid website"
