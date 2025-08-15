import logging
import os
import requests
from services.security.data import Data
from fastapi import HTTPException, status
from models.connection import Connection
from services.oauth.oauth_interface import OauthInterface


class Github(OauthInterface):
    """OAuth client for GitHub API."""

    def __init__(self):
        self.__client_id = os.getenv("GITHUB_CLIENT")
        self.__client_secret = os.getenv("GITHUB_CLIENT_SECRET")

        self.url_oauth = f"https://github.com/login/oauth/authorize?client_id={self.__client_id}&scope=read:user"
        self.url_user_info = "https://api.github.com"

        # Manage access_token
        self.url_get_access_token = "https://github.com/login/oauth/access_token"

    def get_oauth_url(self) -> str:
        return self.url_oauth

    def get_access_token(self, code: str):
        payload = {
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
            "code": code,
        }

        headers = {
            "Accept": "application/json"
        }

        try:
            response = requests.post(self.url_get_access_token, data=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            # {'access_token': '...', 'token_type': 'bearer', 'scope': 'read:user'}
            if data['scope'] == 'read:user':
                return data
            raise Exception('Invalid scope')
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something wrong happened, please try again later"
            ) from e

    def get_user_info(self, connection: Connection):
        """
        Get user data using the access token.
        """
        decrypted_token = Data().decrypt(connection.access_token)
        headers = {'Authorization': f'token {decrypted_token}'}
        url = f"{self.url_user_info}/user"
        try:
            response = requests.get(url=url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something wrong happened, please try again later"
            ) from e

    def get_all_public_projects(self, account_id: int):
        """
        Retrieve all public repositories for a GitHub user by account ID.
        """
        headers = {
            "Accept": "application/vnd.github+json"
        }

        user_url = f"{self.url_user_info}/user/{account_id}"
        try:
            user_response = requests.get(user_url, headers=headers)
            user_response.raise_for_status()
            username = user_response.json().get("login")
            if not username:
                raise HTTPException(status_code=404, detail="Unable to resolve GitHub username from account_id")
        except requests.RequestException as e:
            logging.exception(e)
            raise HTTPException(status_code=502, detail="Failed to contact GitHub API") from e

        repos_url = f"{self.url_user_info}/users/{username}/repos?type=public&sort=updated"
        try:
            repos_response = requests.get(repos_url, headers=headers)
            repos_response.raise_for_status()
            response = []
            for project in repos_response.json():
                response.append({
                    "id": project['id'],
                    "name": project['name'],
                    "language": project['language'],
                    "website": "github",
                    "link": f"https://github.com/{username}/{project['name']}"
                })

            return response
        except requests.RequestException as e:
            logging.exception(e)
            raise HTTPException(status_code=502, detail="Failed to fetch public repositories from GitHub") from e
