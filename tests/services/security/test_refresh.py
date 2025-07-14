import pytest
import datetime
from jwt import encode
from fastapi import HTTPException
from services.security.refresh import Refresh


@pytest.fixture
def refresh_instance():
    return Refresh()


def test_generate_returns_token(refresh_instance):
    token = refresh_instance.generate(123)
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_returns_id_for_valid_token(refresh_instance):
    token = refresh_instance.generate(42)
    user_id = refresh_instance.verify(token)
    assert user_id == 42


def test_verify_expired_token_raises_401(refresh_instance):
    expired_payload = {
        "id": 1,
        "type": "refresh",
        "exp": int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp())
    }
    token = encode(expired_payload, refresh_instance.SECURITY_TOKEN, algorithm="HS256")

    with pytest.raises(HTTPException) as excinfo:
        refresh_instance.verify(token)

    assert excinfo.value.status_code == 401
    assert "expired" in excinfo.value.detail.lower()


def test_verify_invalid_token_raises_400(refresh_instance):
    invalid_token = "this.is.an.invalid.token"

    with pytest.raises(HTTPException) as excinfo:
        refresh_instance.verify(invalid_token)

    assert excinfo.value.status_code == 400
    assert "invalid" in excinfo.value.detail.lower()
