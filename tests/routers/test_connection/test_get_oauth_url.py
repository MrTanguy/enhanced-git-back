import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock
from services.oauth.github import Github
from services.security.bearer import Bearer

client = TestClient(app)

VALID_BEARER_TOKEN = "valid_token"
INVALID_BEARER_TOKEN = "invalid_token"


@pytest.fixture
def mock_bearer_verify():
    with patch.object(Bearer, "verify") as mock_verify:
        def side_effect(token):
            if token != VALID_BEARER_TOKEN:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            return {"id": 123}
        mock_verify.side_effect = side_effect
        yield mock_verify


def test_get_oauth_url_returns_200_with_valid_website(mock_bearer_verify):
    with patch("routers.connection.init_website_service") as mock_init:
        mock_service = MagicMock(spec=Github)
        mock_service.getOauthUrl.return_value = "https://oauth.example.com/auth"
        mock_init.return_value = mock_service

        response = client.get(
            "/connect/url",
            headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"},
            params={"website": "github"}
        )

        assert response.status_code == 200
        assert response.json() == "https://oauth.example.com/auth"
        mock_init.assert_called_once_with(website="github")
        mock_service.getOauthUrl.assert_called_once()


def test_get_oauth_url_returns_401_with_invalid_token(mock_bearer_verify):
    response = client.get(
        "/connect/url",
        headers={"Authorization": f"Bearer {INVALID_BEARER_TOKEN}"},
        params={"website": "github"}
    )

    assert response.status_code == 401


def test_get_oauth_url_returns_400_with_unknown_website(mock_bearer_verify):
    with patch("routers.connection.init_website_service", side_effect=HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid website"
    )):
        response = client.get(
            "/connect/url",
            headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"},
            params={"website": "unknown"}
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid website"}


def test_get_oauth_url_returns_422_when_website_param_is_missing(mock_bearer_verify):
    response = client.get(
        "/connect/url",
        headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"}
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "website"]
