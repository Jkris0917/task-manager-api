import pytest
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user(db):
    user = User.objects.create_user(
        username='testuser',
        password = 'testpass123',
        email = 'test@example.com'
    )
    return user

@pytest.fixture
def auth_client(test_user):
    client = APIClient()
    token = Token.objects.create(user=test_user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client, test_user



