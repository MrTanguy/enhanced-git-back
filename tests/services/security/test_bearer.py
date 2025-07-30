import pytest
from fastapi import HTTPException
from jwt import encode
from services.security.bearer import Bearer
import datetime

@pytest.fixture
def bearer():
    return Bearer()

def test_generate_returns_token(bearer):
    token = bearer.generate(123)
    assert isinstance(token, str)
    # Le token doit être décodable sans erreur
    payload = bearer.verify(token)
    assert payload["id"] == 123
    assert payload["type"] == "bearer"

def test_verify_valid_token_returns_payload(bearer):
    payload = {"id": 42, "type": "bearer", "exp": datetime.datetime.now() + datetime.timedelta(hours=1)}
    token = encode(payload, bearer.security_token, algorithm="HS256")
    result = bearer.verify(token)
    assert result["id"] == 42

def test_verify_expired_token_raises_401(bearer):
    expired_payload = {
        "id": 1,
        "type": "bearer",
        "exp": int((datetime.datetime.now() - datetime.timedelta(hours=1)).timestamp())
    }
    token = encode(expired_payload, bearer.security_token, algorithm="HS256")
    with pytest.raises(HTTPException) as excinfo:
        bearer.verify(token)
    assert excinfo.value.status_code == 401
    assert "expired" in excinfo.value.detail.lower()

def test_verify_invalid_token_raises_400(bearer):
    invalid_token = "invalid.token.string"
    with pytest.raises(HTTPException) as excinfo:
        bearer.verify(invalid_token)
    assert excinfo.value.status_code == 400
    assert "invalid" in excinfo.value.detail.lower()

def test_get_user_id_returns_id(monkeypatch, bearer):
    # On va patcher verify pour contrôler ce qu'elle retourne
    monkeypatch.setattr(bearer, "verify", lambda token: {"id": 99, "type": "bearer"})
    user_id = bearer.get_user_id("anytoken")
    assert user_id == 99
