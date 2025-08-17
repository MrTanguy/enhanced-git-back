from abc import ABC, abstractmethod

from models.connection import Connection


class OauthInterface(ABC):
    """Abstract base class for OAuth provider implementations."""

    @abstractmethod
    def get_oauth_url(self):
        """Get the OAuth URL."""

    @abstractmethod
    def get_access_token(self, code: str):
        """Called after the callback, get the access token from the callback code."""

    @abstractmethod
    def get_user_info(self, connection: Connection):
        """Get user data using the access token."""

    @abstractmethod
    def get_all_public_projects(self, account_id: str):
        """Get all public repositories for the given username."""
