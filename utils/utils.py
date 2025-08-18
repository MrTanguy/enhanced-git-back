import re

from fastapi import HTTPException, status
from services.oauth.gitlab import Gitlab
from services.oauth.github import Github
from services.oauth.oauth_interface import OauthInterface


def is_username_valid(username: str) -> bool:
    """
    Validate if the username is a valid email address.

    :param username: the username string to validate
    :return: True if valid, False otherwise
    """
    regex = r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(regex, username))


def is_password_valid(password: str) -> bool:
    """
    Validate password complexity:
    Minimum 8 characters, at least one uppercase, one lowercase, one digit and one special character.

    :param password: the password string to validate
    :return: True if valid, False otherwise
    """
    regex = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    return bool(re.match(regex, password))


def init_website_service(website: str) -> OauthInterface:
    """
    Initialize the OAuth service based on the website name.

    :param website: name of the OAuth provider (e.g., 'github')
    :return: an instance of the corresponding OauthInterface implementation
    :raises HTTPException: if the provider is not supported
    """
    if website == "github":
        return Github()
    if website == "gitlab":
        return Gitlab()
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"This authentication provider is not supported : {website}"
    )
