from fastapi import status, HTTPException
from fastapi.testclient import TestClient

from main import app
from repositories.UserRepository import UserRepository
from services.security.bearer import Bearer
from services.security.refresh import Refresh

client = TestClient(app)

def test_login_valid_credentials(mocker):
    
    mock_user = mocker.MagicMock()
    mock_user.id = 1

    mocker.patch.object(UserRepository, "login", return_value=mock_user)
    mocker.patch.object(Bearer, 'generate', return_value="fake_bearer_token")
    mocker.patch.object(Refresh, 'generate', return_value="fake_refresh_token")

    response = client.post(
        "/auth/token", 
        data={
            "username": "valid_user@test.com", 
            "password": "Valid@Password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"bearer": "fake_bearer_token"} 
    assert "refresh" in response.cookies


def test_login_invalid_credentials(mocker):

    mocker.patch.object(UserRepository, "login", return_value=None)

    response = client.post(
        "/auth/token",
        data={
            "username": "invalid_user@test.com", 
            "password": "WrongPassword@123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid credentials"


def test_login_invalid_data():
    
    response = client.post(
        "/auth/token",
        data={
            "username": "valid_user@test.com",
            "password": "invalid-password" 
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Please enter a strong password"

    response = client.post(
        "/auth/token",
        data={
            "username": "invalid-email",
            "password": "Valid@Password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Please enter a valid email address"


def test_login_raises_http_exception(mocker):
    mocker.patch.object(UserRepository, "login", side_effect=HTTPException(status_code=400, detail="Bad Request"))

    response = client.post(
        "/auth/token",
        data={"username": "error_user@test.com", "password": "Valid@Password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Bad Request"


def test_login_internal_server_error(mocker):
    mocker.patch.object(UserRepository, "login", side_effect=Exception("Unexpected error"))

    response = client.post(
        "/auth/token",
        data={"username": "user@test.com", "password": "Valid@Password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"