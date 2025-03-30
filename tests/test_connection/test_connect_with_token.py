import pytest
import logging
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock
from services.oauth.github import Github
from services.security.bearer import Bearer
from repositories.ConnectionRepository import ConnectionRepository

client = TestClient(app)

VALID_BEARER_TOKEN = "valid_token"
INVALID_BEARER_TOKEN = "invalid_token"
VALID_CODE = "valid_code"
INVALID_CODE = "invalid_code"
VALID_USER_ID = 123
VALID_ACCOUNT_ID = 456
MOCK_ACCESS_TOKEN = "mock_access_token"


@pytest.fixture
def mock_bearer_verify():
    """Mock de Bearer.verify() pour simuler l'authentification."""
    with patch.object(Bearer, "verify") as mock_verify:
        def mock_verify_side_effect(token):
            if token != VALID_BEARER_TOKEN:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            return {"id": VALID_USER_ID} 

        mock_verify.side_effect = mock_verify_side_effect
        yield mock_verify


@pytest.fixture
def mock_init_website_service():
    """Mock de init_website_service() pour simuler le service OAuth."""
    with patch("api.connection.init_website_service") as mock_init:
        mock_service = MagicMock(spec=Github)
        mock_service.getAccessToken.return_value = MOCK_ACCESS_TOKEN
        mock_service.getUserInfo.return_value = {"id": VALID_ACCOUNT_ID}
        mock_init.return_value = mock_service
        yield mock_init


@pytest.fixture
def mock_connection_repository():
    """Mock de ConnectionRepository().create pour éviter d'écrire en base de données."""
    with patch.object(ConnectionRepository, "create") as mock_create:
        yield mock_create


def test_connect_with_token_success(mock_bearer_verify, mock_init_website_service, mock_connection_repository):
    """Test succès : utilisateur connecté avec succès."""
    response = client.post(
        "/connect/token",
        headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"},
        data={"code": VALID_CODE, "website": "github"}
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Successfully connected."}


def test_connect_with_token_invalid_token(mock_bearer_verify):
    """Test échec : le token Bearer est invalide."""
    response = client.post(
        "/connect/token",
        headers={"Authorization": f"Bearer {INVALID_BEARER_TOKEN}"},
        data={"code": VALID_CODE, "website": "github"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


def test_connect_with_token_invalid_website(mock_bearer_verify):
    """Test échec : site non reconnu."""
    with patch("api.connection.init_website_service", 
               side_effect=HTTPException(
                   status_code=status.HTTP_400_BAD_REQUEST,
                   detail="Invalid website"
               )):
        response = client.post(
            "/connect/token",
            headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"},
            data={"code": VALID_CODE, "website": "unknown_site"}
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid website"


def test_connect_with_token_invalid_code(mock_bearer_verify, mock_init_website_service):
    """Test échec : code OAuth invalide, donc aucun access token récupéré."""
    with patch("api.connection.init_website_service") as mock_init:
        mock_service = MagicMock(spec=Github)
        mock_service.getAccessToken.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid authorization code"
        )  # Simule une erreur lors de la récupération du token en base
        mock_init.return_value = mock_service

        response = client.post(
            "/connect/token",
            headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"},
            data={"code": INVALID_CODE, "website": "github"}
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid authorization code"


def test_connect_with_token_oauth_error(mock_bearer_verify, mock_init_website_service):
    """Test échec : erreur lors du processus OAuth."""
    with patch("api.connection.init_website_service") as mock_init:
        mock_service = MagicMock(spec=Github)
        mock_service.getAccessToken.side_effect = Exception("OAuth error")  # Simule une erreur OAuth
        mock_init.return_value = mock_service

        response = client.post(
            "/connect/token",
            headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"},
            data={"code": VALID_CODE, "website": "github"}
        )

        assert response.status_code == 500
        assert response.json()["detail"] == "An error occurred during the OAuth token process"
