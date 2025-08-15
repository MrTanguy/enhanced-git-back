import logging
import os

from fastapi import HTTPException, status
import requests
from models.connection import Connection
from repositories.connection_repository import ConnectionRepository
from services.oauth.oauth_interface import OauthInterface
from services.security.data import Data


class Gitlab(OauthInterface):
    """OAuth client for GitLab API."""

    def __init__(self):
        self.__client_id = os.getenv("GITLAB_CLIENT")
        self.__client_secret = os.getenv("GITLAB_CLIENT_SECRET")
        self.__redirect_url = os.getenv("GITLAB_REDIRECT_URL")

        self.url_oauth = (
            f"https://gitlab.com/oauth/authorize"
            f"?client_id={self.__client_id}"
            f"&redirect_uri={self.__redirect_url}"
            f"&response_type=code"
            f"&scope=read_user"
        )
        # https://gitlab.com/api/v4/users/:user_id/projects?visibility=public
        self.url_user_info = "https://gitlab.com/api/v4"

        # Manage access_token
        self.url_get_access_token = "https://gitlab.com/oauth/token"

    def get_oauth_url(self):
        """Get the OAuth URL."""
        return self.url_oauth

    def get_access_token(self, code: str):
        """Called after the callback, get the access token from the callback code."""
        payload = {
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.__redirect_url
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        try:
            response = requests.post(self.url_get_access_token, data=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            # {'access_token': '...', 'token_type': 'Bearer', 'expires_in': 7200, 'refresh_token': '...', 'scope': 'read_user', 'created_at': 1754088949} # pylint: disable=line-too-long
            if data['scope'] == 'read_user':
                return data
            raise Exception('Invalid scope')
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something wrong happened, please try again later"
            ) from e

    def get_user_info(self, connection: Connection):
        """Get user data using the access token."""
        decrypted_token = Data().decrypt(connection.access_token)
        headers = {"Authorization": f"Bearer {decrypted_token}"}
        url = f"{self.url_user_info}/user"
        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 401:
                new_access_token = self.refresh_gitlab_token(connection)

                if not new_access_token:
                    raise HTTPException(status_code=401, detail="Unable to refresh token")
                headers["Authorization"] = f"Bearer {new_access_token}"
                response = requests.get(url, headers=headers, timeout=10)

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch GitLab user info"
            ) from e

    def get_all_public_projects(self, account_id: str):
        """
        Retrieve all public projects for a GitLab user by account ID.
        :param account_id: GitLab user ID
        """
        projects_url = f"https://gitlab.com/api/v4/users/{account_id}/projects"
        params = {
            "visibility": "public",
            "order_by": "updated_at",
            "sort": "desc",
            "per_page": 100
        }

        headers = {
            "Accept": "application/json"
        }

        try:
            response = requests.get(projects_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            projects_data = response.json()

            response_list = []
            for project in projects_data:
                response_list.append({
                    "id": project["id"],
                    "name": project["name"],
                    "language": project.get("language"),
                    "website": "gitlab",
                    "link": project["web_url"]
                })

            return response_list

        except requests.RequestException as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to fetch public projects from GitLab"
            ) from e


    def refresh_gitlab_token(self, connection: Connection) -> str | None:
        """Refresh GitLab access token using the refresh token."""

        data_security = Data()
        decrypted_token = data_security.decrypt(connection.refresh_token)
        data = {
            "grant_type": "refresh_token",
            "refresh_token": decrypted_token,
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
        }
        try:
            conn_repo = ConnectionRepository()
            response = requests.post("https://gitlab.com/oauth/token", data=data, timeout=10)
            if response.status_code == 200:
                token_data = response.json()
                connection = conn_repo.get_by_encrypted_refresh(connection.refresh_token)
                if connection:
                    connection.access_token =  data_security.encrypt(token_data["access_token"])
                    connection.refresh_token = data_security.encrypt(token_data["refresh_token"])
                    conn_repo.update_by_id(connection)

                return token_data["access_token"]

            elif response.status_code == 400 and response.json().get("error") == "invalid_grant":
                conn_repo.delete_by_id(connection.id)
                raise HTTPException(status_code=400, detail="Your GitLab connection has expired. Please reconnect to continue.")
            else:
                logging.error(f"Unexpected error refreshing token: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logging.exception(e)
            return None
