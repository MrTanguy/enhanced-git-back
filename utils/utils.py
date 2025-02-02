import re

from fastapi import HTTPException, status
from services.oauth.github import Github
from services.oauth.oauthInterface import OauthInterface

def is_username_valid(username):
    regex = r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(regex, username))

def is_password_valid(password):
    regex = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    return bool(re.match(regex, password))

def init_website_service(website: str) -> OauthInterface:
    if website == "github":
        return Github()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This authentication provider is not supported : {website}"
        )
