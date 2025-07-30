import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from main import app
from services.security.bearer import Bearer

client = TestClient(app)

VALID_BEARER_TOKEN = "valid_token"
VALID_USER_ID = 123
VALID_UUID = "01HZX9D2B1TVEMD7AFQ9C9RGM5"
INVALID_UUID = "not-exist"

@pytest.fixture
def mock_bearer_verify():
    with patch.object(Bearer, "verify") as mock_verify:
        def side_effect(token):
            if token != VALID_BEARER_TOKEN:
                raise HTTPException(status_code=401, detail="Invalid token")
            return {"id": VALID_USER_ID}
        mock_verify.side_effect = side_effect
        yield mock_verify

@pytest.fixture
def mock_portfolio_repo():
    with patch("routers.portfolio.PortfolioRepository") as mock:
        yield mock

def test_delete_portfolio_success(mock_bearer_verify, mock_portfolio_repo):
    mock_instance = mock_portfolio_repo.return_value
    mock_instance.get_by_uuid.return_value = MagicMock(user_id=VALID_USER_ID)

    headers = {"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    response = client.delete(f"/portfolio/{VALID_UUID}", headers=headers)

    assert response.status_code == 200 or response.status_code == 204

def test_delete_portfolio_forbidden(mock_bearer_verify, mock_portfolio_repo):
    mock_instance = mock_portfolio_repo.return_value
    mock_instance.get_by_uuid.return_value = MagicMock(user_id=999)  # autre utilisateur

    headers = {"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    response = client.delete(f"/portfolio/{VALID_UUID}", headers=headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to modify this resource"

def test_delete_portfolio_not_found(mock_bearer_verify, mock_portfolio_repo):
    mock_instance = mock_portfolio_repo.return_value
    mock_instance.get_by_uuid.side_effect = HTTPException(status_code=404, detail="Portfolio not found")

    headers = {"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    response = client.delete(f"/portfolio/{INVALID_UUID}", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Portfolio not found"

def test_delete_portfolio_internal_error(mock_bearer_verify, mock_portfolio_repo):
    mock_instance = mock_portfolio_repo.return_value
    mock_instance.get_by_uuid.return_value = MagicMock(user_id=VALID_USER_ID)
    mock_instance.delete.side_effect = Exception("Database failure")

    headers = {"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    response = client.delete(f"/portfolio/{VALID_UUID}", headers=headers)

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
