import pytest
from django.contrib.auth.models import User
from bearings.models import Client


@pytest.mark.django_db
class TestClientModel:
    def test_create_client_with_user(self):
        user = User.objects.create_user(username='u1', password='pass')
        client = Client.objects.create(user=user, name='Иван', phone='89990001122')
        assert client.id is not None
        assert client.user == user
        assert client.name == 'Иван'

    def test_create_client_without_user(self):
        client = Client.objects.create(name='Пётр', phone='89990003344')
        assert client.user is None

    def test_client_str(self):
        client = Client.objects.create(name='Пётр', phone='8999')
        assert str(client)