from abc import ABC, abstractmethod

class OauthInterface(ABC):

    @abstractmethod
    def getOauthUrl(self):
        """ Get the ouath url """
        pass
    
    @abstractmethod
    def getAccessToken(self, code: str):
        """ Called after the callback, get the access_token from the callback code """
        pass

    @abstractmethod
    def getUserInfo(self, access_token: str):
        """ Get user data """
        pass

    @abstractmethod
    def getAllPublicProjects(self, username: str):
        """ Get all public repository """
        pass
