import logging
import os
import requests
from fastapi import HTTPException, status
from services.oauth.oauthInterface import OauthInterface

class Github(OauthInterface):

    def __init__(self):
        self.__client_id = os.getenv("GITHUB_CLIENT")
        self.__client_secret = os.getenv("GITHUB_CLIENT_SECRET")

        self.url_oauth = f"https://github.com/login/oauth/authorize?client_id={self.__client_id}&scope=user"
        self.url_user_info = "https://api.github.com"

        # Manage access_token
        self.url_get_access_token = "https://github.com/login/oauth/access_token"
        self.url_delete_access_token = f"https://api.github.com/applications/{self.__client_id}/token"

    def getOauthUrl(self) -> str:
        return self.url_oauth
    
    def getAccessToken(self, code: str):

        payload = {
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
            "code": code,
        }

        headers = {
            "Accept": "application/json"
        }

        try:
            response = requests.post(self.url_get_access_token, data=payload, headers=headers)
            response.raise_for_status()

            data = response.json()

            return data['access_token']

        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something wrong happened, please try again later"
            )

    def getUserInfo(self, access_token: str):
        headers = {'Authorization': f'token {access_token}'}
        url = f"{self.url_user_info}/user"
        try:
            response = requests.get(url=url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something wrong happened, please try again later"
            )
        
    def deleteAccessToken(self, access_token: str):
        try:
            headers = {
                "Authorization": f"token {access_token}"
            }

            requests.delete(self.url_delete_access_token, headers=headers)

        except Exception as e:
            pass

    def getAllPublicProjects(self, account_id: int):
        """
        Récupère tous les dépôts publics du compte GitHub en utilisant son ID unique.
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
            raise HTTPException(status_code=502, detail="Failed to contact GitHub API")

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
                    "link": f"https://github.com/{username}/{project['name']}"
                })
            
            # print(repos_response.json())
            return response
        except requests.RequestException as e:
            logging.exception(e)
            raise HTTPException(status_code=502, detail="Failed to fetch public repositories from GitHub")
