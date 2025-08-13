import logging
import os

from fastapi import HTTPException, status
import requests
from services.oauth.oauth_interface import OauthInterface


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
        self.url_user_info = "https://gitlab.com/api/v4/"

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
            "Accept": "application/json"
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

    def get_user_info(self, access_token: str):
        """Get user data using the access token."""
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"{self.url_user_info}/user"
        try:
            logging.info(url)
            response = requests.get(url=url, headers=headers, timeout=10)
            response.raise_for_status()
            if response.status_code == 401:
                pass
                # self.refresh_gitlab_token()


            return response.json()
        except requests.exceptions.RequestException as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something wrong happened, please try again later"
            ) from e

    def get_all_public_projects(self, account_id: str):
        """Get all public repositories for the given username."""
        # url = f"{self.get_user_info}/user/{account_id}"
        # try:
        #     response = requests.get(url=url)
        # except requests.RequestException as e:
        #     logging.exception(e)
        #     raise HTTPException(status_code=502, detail="Failed to contact GitLab API") from e
        # projects_response = requests.get(
        #     f"https://gitlab.com/api/v4/users/{user_id}/projects",
        #     headers={"Authorization": f"Bearer {access_token}"},
        #     params={"visibility": "public"}
        # )

        # projects_response.raise_for_status()
        # projects = projects_response.json()

        # for project in projects:
        #     print(f"- {project['name']} ({project['web_url']})")

    # def refresh_gitlab_token(self):
    #     data = {
    #         "grant_type": "refresh_token",
    #         "refresh_token": connection.refresh_token,
    #         "client_id": CLIENT_ID,
    #         "client_secret": CLIENT_SECRET,
    #     }
    #     response = requests.post("https://gitlab.com/oauth/token", data=data)
    #     if response.status_code == 200:
    #         token_data = response.json()
    #         connection.access_token = token_data["access_token"]
    #         connection.refresh_token = token_data["refresh_token"]
    #         connection.expires_in = token_data["expires_in"]
    #         db.commit()
    #         return connection.access_token
    #     else:
    #         # Si c’est une erreur liée au refresh_token, invalider la connexion
    #         if response.status_code == 400 and response.json().get("error") == "invalid_grant":
    #             print("Refresh token invalide ou expiré.")
    #             # Ici, soit tu supprimes la connexion, soit tu la désactives
    #             db.delete(connection)
    #             db.commit()
    #         return None
