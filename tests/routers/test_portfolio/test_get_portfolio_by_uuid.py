import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from main import app

client = TestClient(app)

VALID_UUID = "01HZX9D2B1TVEMD7AFQ9C9RGM5"
INVALID_UUID = "does-not-exist"

@pytest.fixture
def mock_get_by_uuid():
    with patch("routers.portfolio.PortfolioRepository.get_by_uuid") as mock:
        yield mock


def test_get_portfolio_success(mock_get_by_uuid):
    # Simule un portfolio trouvé
    mock_get_by_uuid.return_value = {
        "uuid": VALID_UUID,
        "user_id": 123,
        "title": "My Portfolio",
        "content": []
    }

    response = client.get(f"/portfolio/{VALID_UUID}")

    assert response.status_code == 200
    data = response.json()
    assert data["uuid"] == VALID_UUID
    assert data["title"] == "My Portfolio"


def test_get_portfolio_not_found(mock_get_by_uuid):
    # Simule un portfolio non trouvé
    mock_get_by_uuid.side_effect = HTTPException(status_code=404, detail="Portfolio not found")

    response = client.get(f"/portfolio/{INVALID_UUID}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Portfolio not found"


def test_get_portfolio_server_error(mock_get_by_uuid):
    # Simule une erreur inattendue (ex: base de données indisponible)
    mock_get_by_uuid.side_effect = Exception("Unexpected error")

    response = client.get(f"/portfolio/{VALID_UUID}")

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
