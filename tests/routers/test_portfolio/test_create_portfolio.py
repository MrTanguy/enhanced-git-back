import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from main import app
from services.security.bearer import Bearer
from repositories.portfolio_repository import PortfolioRepository

client = TestClient(app)

VALID_BEARER_TOKEN = "valid_token"
VALID_USER_ID = 123


@pytest.fixture
def mock_bearer_verify():
    with patch.object(Bearer, "verify") as mock_verify:
        mock_verify.side_effect = lambda token: {"id": VALID_USER_ID}
        yield mock_verify


@pytest.fixture
def mock_portfolio_create():
    with patch.object(PortfolioRepository, "create") as mock_create:
        fake_portfolio = {
            "uuid": "01HZX9D2B1TVEMD7AFQ9C9RGM5",
            "user_id": VALID_USER_ID,
            "title": "New Portfolio",
            "content": []
        }
        mock_create.return_value = fake_portfolio
        yield mock_create


def test_create_portfolio_success(mock_bearer_verify, mock_portfolio_create):
    response = client.get(
        "/portfolio/create",
        headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    )

    assert response.status_code == 200
    json_data = response.json()

    assert json_data["user_id"] == VALID_USER_ID
    assert json_data["title"] == "New Portfolio"
    assert isinstance(json_data["content"], list)


def test_create_portfolio_server_error(mock_bearer_verify):
    with patch.object(PortfolioRepository, "create", side_effect=Exception("boom")):
        response = client.get(
            "/portfolio/create",
            headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
        )
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"
