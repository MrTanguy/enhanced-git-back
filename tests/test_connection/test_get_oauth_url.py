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
        def mock_verify_side_effect(token):
            if token != VALID_BEARER_TOKEN:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )  # Lever une HTTPException pour simuler le comportement réel
        mock_verify.side_effect = mock_verify_side_effect
        yield mock_verify


@pytest.fixture
def mock_init_website_service():
    with patch("api.connection.init_website_service") as mock_init:
        mock_github_instance = MagicMock(spec=Github) 
        mock_github_instance.getOauthUrl.return_value = "https://oauth.example.com/auth"
        mock_init.return_value = mock_github_instance 
        yield mock_init

def test_get_oauth_url_success(mock_bearer_verify, mock_init_website_service):
    response = client.get(
        "connect/url",
        headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"},
        params={"website": "github"}
    )
    assert response.status_code == 200
    assert response.json() == "https://oauth.example.com/auth"
    

def test_get_oauth_url_invalid_token(mock_bearer_verify):
    response = client.get(
        "/connect/url",
        headers={"Authorization": f"Bearer {INVALID_BEARER_TOKEN}"},
        params={"website": "github"}
    )
    assert response.status_code == 401 


def test_get_oauth_url_invalid_website(mock_bearer_verify):
    """Test échec : site non reconnu."""
    with patch("api.connection.init_website_service", 
               side_effect=HTTPException(
                   status_code=status.HTTP_400_BAD_REQUEST,
                   detail="Invalid website"
               )):
        response = client.get(
            "/connect/url",
            headers={"Authorization": f"Bearer {VALID_BEARER_TOKEN}"},
            params={"website": "unknown_site"}
        )
        print(response.json()) 
        assert response.status_code == 400
