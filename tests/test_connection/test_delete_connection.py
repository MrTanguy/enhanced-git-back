import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from main import app 
from repositories.ConnectionRepository import ConnectionRepository
from services.security.bearer import Bearer

client = TestClient(app)

VALID_BEARER_TOKEN = "valid_token"
INVALID_BEARER_TOKEN = "invalid_token"
VALID_USER_ID = 123

@pytest.fixture
def mock_connection_repo():
    """Mock la classe ConnectionRepository dans le bon contexte."""
    with patch("api.connection.ConnectionRepository") as mock_repo:
        mock_instance = mock_repo.return_value
        mock_instance.delete.return_value = None
        yield mock_instance

@pytest.fixture
def mock_bearer_verify():
    """Mock de Bearer.verify() pour simuler l'authentification."""
    with patch("services.security.bearer.Bearer.verify") as mock_verify:
        def mock_verify_side_effect(token):
            if token != VALID_BEARER_TOKEN:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            return {"id": VALID_USER_ID}

        mock_verify.side_effect = mock_verify_side_effect
        yield mock_verify

def test_delete_connection_success(mock_connection_repo, mock_bearer_verify):
    response = client.delete(
        "/connect/delete/123", 
        headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    )
    assert response.status_code == 200
    mock_connection_repo.delete.assert_called_once_with(VALID_USER_ID, 123)

def test_delete_connection_invalid_token(mock_connection_repo, mock_bearer_verify):
    response = client.delete(
        "/connect/delete/123", 
        headers={"Authorization": f"Bearer {INVALID_BEARER_TOKEN}"}
    )
    assert response.status_code == 401

def test_delete_connection_not_found(mock_connection_repo, mock_bearer_verify):
    """Test si la connexion à supprimer n'existe pas"""
    mock_connection_repo.delete.side_effect = HTTPException(status_code=404, detail="Not Found")

    response = client.delete(
        "/delete/123", 
        headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}

def test_delete_connection_internal_error(mock_connection_repo, mock_bearer_verify):
    """Test si une erreur interne se produit lors de la suppression"""
    mock_connection_repo.delete.side_effect = Exception("Unexpected error")

    response = client.delete(
        "connect/delete/123",
        headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "An error occurred during the process"}
