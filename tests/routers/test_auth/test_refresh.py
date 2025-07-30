import pytest

from fastapi import status, HTTPException
from fastapi.testclient import TestClient

from main import app
from services.security.refresh import Refresh

client = TestClient(app)


def test_refresh_invalid_token(mocker):

    mocker.patch.object(Refresh, "verify", side_effect=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"))

    client.cookies.set("refresh", "invalid_refresh_token")

    response = client.get("/auth/refresh")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid refresh token"


def test_refresh_missing_token():

    client.cookies.clear()

    response = client.get("/auth/refresh")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Refresh token is missing"
