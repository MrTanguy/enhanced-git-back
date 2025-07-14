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
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            return {"id": VALID_USER_ID}
        mock_verify.side_effect = side_effect
        yield mock_verify

@pytest.fixture
def mock_portfolio_repo():
    with patch("routers.portfolio.PortfolioRepository") as mock:
        yield mock


def test_update_portfolio_success(mock_bearer_verify, mock_portfolio_repo):
    mock_instance = mock_portfolio_repo.return_value
    mock_instance.get_by_uuid.return_value = MagicMock(user_id=VALID_USER_ID)
    mock_instance.update.return_value = {
        "uuid": VALID_UUID,
        "user_id": VALID_USER_ID,
        "title": "Updated Title",
        "content": []
    }

    update_data = {
        "title": "Updated Title",
        "content": []
    }

    headers = {"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    response = client.patch(f"/portfolio/{VALID_UUID}", json=update_data, headers=headers)

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


def test_update_portfolio_forbidden(mock_bearer_verify, mock_portfolio_repo):
    mock_instance = mock_portfolio_repo.return_value
    mock_instance.get_by_uuid.return_value = MagicMock(user_id=999)

    update_data = {
        "title": "Title",
        "content": []
    }

    headers = {"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    response = client.patch(f"/portfolio/{VALID_UUID}", json=update_data, headers=headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to modify this resource"


def test_update_portfolio_not_found(mock_bearer_verify, mock_portfolio_repo):
    mock_instance = mock_portfolio_repo.return_value
    mock_instance.get_by_uuid.side_effect = HTTPException(status_code=404, detail="Portfolio not found")

    update_data = {
        "title": "Title",
        "content": []
    }

    headers = {"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    response = client.patch(f"/portfolio/{INVALID_UUID}", json=update_data, headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Portfolio not found"


def test_update_portfolio_server_error(mock_bearer_verify, mock_portfolio_repo):
    mock_instance = mock_portfolio_repo.return_value
    mock_instance.get_by_uuid.return_value = MagicMock(user_id=123)
    mock_instance.update.side_effect = Exception("DB crash")

    update_data = {
        "title": "Title",
        "content": []
    }

    headers = {"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    response = client.patch(f"/portfolio/{VALID_UUID}", json=update_data, headers=headers)

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"

def test_update_portfolio_http_exception_propagation(mock_bearer_verify, mock_portfolio_repo):
    mock_instance = mock_portfolio_repo.return_value
    mock_instance.get_by_uuid.return_value = MagicMock(user_id=VALID_USER_ID)
    mock_instance.update.side_effect = HTTPException(status_code=422, detail="Invalid data")

    update_data = {
        "title": "Invalid data", 
        "content": []
    }

    headers = {"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    response = client.patch(f"/portfolio/{VALID_UUID}", json=update_data, headers=headers)

    print(response.json())

    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid data"

