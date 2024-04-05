import json
import unittest

from django.test import TestCase, RequestFactory
from rest_framework import status
from django.contrib.auth.models import User

from api.models import Room
from api.views import JoinRoom


class ApiViewTest(TestCase):
    def setUp(self):
        super(ApiViewTest, self).setUp()
        self.factory = RequestFactory()
        # Authenticate the user
        self.user = User.objects.create_user(username='Peter Parker',
                                             password='idontfeelsogood')
        self.client.login(username='Peter Parker', password='idontfeelsogood')

    def test_create_room(self):
        data = {
            'guest_can_pause': True,
            'votes_to_skip': 5
        }
        response = self.client.post('/api/create-room', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('room_code' in self.client.session)

        # Check values of the room created
        room = Room.objects.get(code=self.client.session['room_code'])
        self.assertEqual(room.guest_can_pause, data['guest_can_pause'])
        self.assertEqual(room.votes_to_skip, data['votes_to_skip'])

    def test_join_room_success(self):
        room = Room.objects.create()
        room_code = room.code

        # Prepare POST request
        data = {'code': room_code}
        response = self.client.post('/api/join-room', data, format='json')

        # Check response status and content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'Room Joined!'})
        self.assertEqual(self.client.session['room_code'], room_code)

    def test_join_room_invalid_code(self):
        # Prepare POST request
        data = {'code': 'wrong-code'}
        response = self.client.post('/api/join-room', data, format='json')

        # Check response status and content
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data,
                         {'Bad Request': 'Invalid Room Code.'})

    def test_join_room_missing_code(self):
        # Prepare POST request
        data = {}
        response = self.client.post('/api/join-room', data, format='json')

        # Check response status and content
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data,
                         {
                             'Bad Request': 'Invalid post data, did not find '
                                            'a code key'})

    def test_get_room_success(self):
        # Create a mock Room object
        room = Room.objects.create(host='ix900kxmse63dgfr6t35eja1lusw3bm7')
        room_code = room.code

        # Make a GET request with valid room code
        response = self.client.get('/api/get-room',
                                   {'code': room_code})

        # Check response status and content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], room_code)

    def test_get_room_invalid_code(self):
        # Make a GET request with invalid room code
        response = self.client.get('/api/get-room',
                                   {'code': 'invalid_code'})

        # Check response status and content
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data,
                         {'Room Not Found': 'Invalid Room Code.'})

    def test_get_room_missing_code(self):
        # Make a GET request without room code
        response = self.client.get('/api/get-room')

        # Check response status and content
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
            'Bad Request': 'Code parameter not found in request'})

    def test_user_in_room(self):
        # Make a GET request to user-in-room endpoint
        response = self.client.get('/api/user-in-room')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_leave_room_success(self):
        # Mock a room with the host's session key
        host_session_key = self.client.session.session_key
        room = Room.objects.create(host=host_session_key)
        client_session = self.client.session
        client_session['room_code'] = room.code
        client_session.save()

        # Make a POST request to leave-room endpoint
        response = self.client.post('/api/leave-room')

        # Check response status and content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'Message': 'Success'})

        # Check if room is deleted
        self.assertFalse(Room.objects.filter(host=host_session_key).exists())


    def test_update_room_success(self):
        # Create a mock room and session
        host = self.client.session.session_key

        room = Room.objects.create(host=host)

        session = self.client.session
        session['room_code'] = room.code
        session.save()

        # Prepare patch request data
        patch_data = {
            'guest_can_pause': True,
            'votes_to_skip': 3,
            'code': room.code
        }

        # Set session data on the client
        self.client.cookies['sessionid'] = session.session_key

        # Make a patch request to update-room endpoint
        response = self.client.patch('/api/update-room', data=patch_data,
                                     content_type='application/json')

        # Check response status and content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['guest_can_pause'], True)
        self.assertEqual(response.data['votes_to_skip'], 3)

    def test_update_room_invalid_data(self):
        # Create a mock room and session
        room = Room.objects.create(host='test_host_session_key',
                                   code='test_code')
        session = self.client.session
        session['room_code'] = 'test_code'
        session.save()

        # Prepare invalid patch request data (missing 'code' field)
        patch_data = {
            'guest_can_pause': True,
            'votes_to_skip': 3
        }

        # Set session data on the client
        self.client.cookies['sessionid'] = session.session_key

        # Make a patch request to update-room endpoint
        response = self.client.patch('/api/update-room', data=patch_data,
                                     content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

if __name__ == '__main__':
    unittest.main()
