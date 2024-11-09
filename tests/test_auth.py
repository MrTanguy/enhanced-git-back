import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)

mock_user = {
    "username": "test_user",
    "password": "password123"
}

"""

def test_login_success():
    # Mock pour la méthode `login` de `UserRepository`
    with patch("repositories.UserRepository") as MockUserRepo:
        mock_repo = MockUserRepo.return_value
        mock_repo.login.return_value = mock_user  # Simuler un utilisateur existant
        
        response = client.post("/token", data={
            "username": mock_user["username"],
            "password": mock_user["password"]
        })
        
        # Vérifier la réponse
        assert response.status_code == 200
        assert response.json() == mock_user

def test_login_invalid_credentials():
    # Mock pour simuler un échec de connexion
    with patch("repositories.UserRepository") as MockUserRepo:
        mock_repo = MockUserRepo.return_value
        mock_repo.login.return_value = None  # Aucun utilisateur n'est trouvé
        
        response = client.post("/token", data={
            "username": "invalid_user",
            "password": "wrong_password"
        })
        
        # Vérifier la réponse pour des identifiants invalides
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid credentials"}
"""
        