import pytest
from django.contrib.auth.models import User
from bearings.models import Client
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestClientsAPI:
    @pytest.fixture
    def api(self):
        return APIClient()

    @pytest.fixture
    def admin(self):
        return User.objects.create_superuser(
            username='admin', email='a@a.a', password='adminpass'
        )

    @pytest.fixture
    def regular(self):
        return User.objects.create_user(username='user', password='userpass')

    def test_admin_sees_all(self, api, admin):
        Client.objects.create(name='A', phone='1')
        Client.objects.create(name='B', phone='2')
        api.force_authenticate(user=admin)
        response = api.get('/api/clients/')
        assert response.status_code == 200
        assert len(response.data) == 2

    def test_user_sees_only_own(self, api, regular):
        Client.objects.create(user=regular, name='C', phone='3')
        Client.objects.create(name='D', phone='4')
        api.force_authenticate(user=regular)
        response = api.get('/api/clients/')
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'C'

    def test_create_client_as_admin(self, api, admin):
        api.force_authenticate(user=admin)
        response = api.post('/api/clients/', {'name': 'New', 'phone': '5'})
        assert response.status_code == 201
        assert Client.objects.filter(name='New').exists()