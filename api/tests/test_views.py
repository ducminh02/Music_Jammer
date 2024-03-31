from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from music_jammer.api.models import Room
from music_jammer.api.serializers import CreateRoomSerializer


class CreateRoomViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_room(self):
        data = {
            'guest_can_pause': True,
            'votes_to_skip': 5
        }
        response = self.client.post('/api/create-room/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('room_code' in self.client.session)

        # Check values of the room created
        room = Room.objects.get(code=self.client.session['room_code'])
        self.assertEqual(room.guest_can_pause, data['guest_can_pause'])
        self.assertEqual(room.votes_to_skip, data['votes_to_skip'])


