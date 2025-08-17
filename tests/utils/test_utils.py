import pytest
from fastapi import HTTPException
from services.oauth.github import Github
from services.oauth.gitlab import Gitlab
from utils.utils import is_username_valid, is_password_valid, init_website_service 

def test_is_username_valid():
    assert is_username_valid("test@example.com")
    assert is_username_valid("user.name-123@mail.co.uk")
    assert not is_username_valid("invalid-email")
    assert not is_username_valid("user@invalid@domain.com")
    assert not is_username_valid("user@domain")

def test_is_password_valid():
    assert is_password_valid("StrongP@ss1")
    assert is_password_valid("Abcdef1@")
    assert not is_password_valid("weakpass")
    assert not is_password_valid("NoSpecialChar1")
    assert not is_password_valid("nospecialchar1@") 
    assert not is_password_valid("NOSPECIALCHAR1@")
    assert not is_password_valid("NoNumber@")

def test_init_website_service_github():
    service = init_website_service("github")
    assert isinstance(service, Github)

def test_init_website_service_gitlab():
    service = init_website_service("gitlab")
    assert isinstance(service, Gitlab)

def test_init_website_service_unsupported():
    with pytest.raises(HTTPException) as excinfo:
        init_website_service("unsupported")
    assert excinfo.value.status_code == 400
    assert "not supported" in excinfo.value.detail.lower()
