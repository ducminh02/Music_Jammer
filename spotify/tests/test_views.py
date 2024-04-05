from django.test import TestCase
from rest_framework import status
from unittest.mock import patch

from spotify.views import AuthURL
from django.contrib.auth.models import User


class SpotifyViewTest(TestCase):
    def setUp(self):
        super(SpotifyViewTest, self).setUp()
        # Authenticate the user
        self.user = User.objects.create_user(username='Peter Parker',
                                             password='idontfeelsogood')
        self.client.login(username='Peter Parker', password='idontfeelsogood')

    def test_auth_url_generation(self):
        response = self.client.get('/spotify/get-auth-url')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('url', response.json())
