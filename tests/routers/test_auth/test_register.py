import pytest

from fastapi import status, HTTPException
from fastapi.testclient import TestClient

from main import app
from repositories.user_repository import UserRepository
from services.security.bearer import Bearer
from services.security.refresh import Refresh

client = TestClient(app)


@pytest.mark.parametrize(
    "data",
    [
        ({"username": "valid_user@test.com"}, "password"),
        ({"password": "Valid@Password123"}, "username"),
    ],
)
def test_register_missing_data(data):
    response = client.post(
        "/auth/register",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == "Field required"
  

def test_register_valid_user(mocker):

    mock_user = mocker.MagicMock()
    mock_user.id = 1

    mocker.patch.object(UserRepository, "create", return_value=mock_user)
    mocker.patch.object(Bearer, "generate", return_value="fake_bearer_token")
    mocker.patch.object(Refresh, "generate", return_value="fake_refresh_token")

    response = client.post(
        "/auth/register",
        data={"username": "new_user@test.com", "password": "Valid@Password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"bearer": "fake_bearer_token"}
    assert "refresh" in response.cookies


def test_register_invalid_email():

    response = client.post(
        "/auth/register",
        data={"username": "invalid-email", "password": "Valid@Password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Please enter a valid email address"


def test_register_weak_password():

    response = client.post(
        "/auth/register",
        data={"username": "valid_user@test.com", "password": "123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Please enter a strong password"


def test_register_existing_user(mocker):

    mocker.patch.object(UserRepository, "create", side_effect=HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists."))

    response = client.post(
        "/auth/register",
        data={"username": "existing_user@test.com", "password": "Valid@Password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "User already exists."


def test_register_missing_data():

    response = client.post(
        "/auth/register",
        data={"username": "valid_user@test.com"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == "Field required"

    response = client.post(
        "/auth/register",
        data={"password": "Valid@Password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == "Field required"


def test_register_internal_error(mocker):

    mocker.patch.object(UserRepository, "create", side_effect=HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error."))

    response = client.post(
        "/auth/register",
        data={"username": "new_user@test.com", "password": "Valid@Password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Internal server error."


def test_register_user_creation_failed(mocker):
    mocker.patch.object(UserRepository, "create", return_value=None)
    
    response = client.post(
        "/auth/register",
        data={"username": "user@test.com", "password": "Valid@Password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Please enter a valid email address and a strong password"
    

def test_refresh_valid_token(mocker):

    mocker.patch.object(Refresh, "verify", return_value=1)
    mocker.patch.object(Bearer, "generate", return_value="fake_bearer_token")

    client.cookies.set("refresh", "vvalid_refresh_token") 

    response = client.get("/auth/refresh")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"bearer": "fake_bearer_token"}