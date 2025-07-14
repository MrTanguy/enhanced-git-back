import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch
from services.security.bearer import Bearer

client = TestClient(app)

VALID_BEARER_TOKEN = "valid_token"
INVALID_BEARER_TOKEN = "invalid_token"
VALID_USER_ID = 123


@pytest.fixture
def mock_bearer_verify():
    with patch.object(Bearer, "verify") as mock_verify:
        def mock_side_effect(token):
            if token != VALID_BEARER_TOKEN:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            return {"id": VALID_USER_ID}
        mock_verify.side_effect = mock_side_effect
        yield mock_verify


@pytest.fixture
def mock_connection_repo():
    with patch("routers.connection.ConnectionRepository") as mock_repo:
        instance = mock_repo.return_value
        instance.delete.return_value = None
        yield instance


def test_delete_connection_success(mock_connection_repo, mock_bearer_verify):
    response = client.delete(
        "/connect/delete/123",
        headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    )

    assert response.status_code == 200
    mock_connection_repo.delete.assert_called_once_with(VALID_USER_ID, 123)


def test_delete_connection_returns_401_when_token_is_invalid(mock_connection_repo, mock_bearer_verify):
    response = client.delete(
        "/connect/delete/123",
        headers={"Authorization": f"Bearer {INVALID_BEARER_TOKEN}"}
    )

    assert response.status_code == 401


def test_delete_connection_returns_404_if_not_found(mock_connection_repo, mock_bearer_verify):
    mock_connection_repo.delete.side_effect = HTTPException(status_code=404, detail="Not Found")

    response = client.delete(
        "/connect/delete/123",
        headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_delete_connection_returns_500_on_internal_error(mock_connection_repo, mock_bearer_verify):
    mock_connection_repo.delete.side_effect = Exception("Unexpected error")

    response = client.delete(
        "/connect/delete/123",
        headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "An error occurred during the process"}
