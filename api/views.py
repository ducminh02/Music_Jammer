from django.shortcuts import render
from rest_framework import generics, status

from .models import Room
from .serializers import RoomSerializer, CreateRoomSerializer, \
    UpdateRoomSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse


# See all rooms exists
class RoomView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class GetRoom(APIView):
    serializer_class = RoomSerializer
    lookup_url_kwarg = 'code'

    def get(self, request, format=None):
        code = request.GET.get(self.lookup_url_kwarg)
        if code is not None:
            room = Room.objects.filter(code=code)
            if len(room) > 0:
                data = RoomSerializer(room[0]).data
                data['is_host'] = (self.request.session.session_key ==
                                   room[0].host)
                return Response(data, status=status.HTTP_200_OK)
            return Response({'Room Not Found': 'Invalid Room Code.'},
                            status=status.HTTP_404_NOT_FOUND)

        return Response({'Bad Request':
                             'Code parameter not found in request'},
                        status=status.HTTP_400_BAD_REQUEST)


class JoinRoom(APIView):
    lookup_url_kwarg = 'code'

    def post(self, request, format=None):
        # check if user in a session
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        code = request.data.get(self.lookup_url_kwarg)

        if code is not None:
            room_result = Room.objects.filter(code=code)
            if len(room_result) > 0:
                room = room_result[0]
                self.request.session['room_code'] = code
                return Response({'message': 'Room Joined!'},
                                status=status.HTTP_200_OK)
            return Response({'Bad Request': 'Invalid Room Code.'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {'Bad Request': 'Invalid post data, did not find a code key'},
            status=status.HTTP_400_BAD_REQUEST)


class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer

    def post(self, request, format=None):
        # check if user in a session
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        # serialize the data received from the request
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            host = self.request.session.session_key
            queryset = Room.objects.filter(host=host)

            # check if a room with the session_key alr exists
            if queryset.exists():
                # update the room
                room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
                # add the (randomly created) room code to session of request
                self.request.session['room_code'] = room.code
            else:
                # create a room
                room = Room(host=host, guest_can_pause=guest_can_pause,
                            votes_to_skip=votes_to_skip)
                room.save()
                self.request.session['room_code'] = room.code

            return Response(RoomSerializer(room).data,
                            status=status.HTTP_201_CREATED)

class UserInRoom(APIView):
    def get(self, request, format=None):
        # check if user in a session
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        data = {
            'code': self.request.session.get('room_code')
        }
        # return the randomly generated room code of user
        return JsonResponse(data, status=status.HTTP_200_OK)


class LeaveRoom(APIView):
    def post(self, request, format=None):
        # check if room code is in session
        if 'room_code' in self.request.session:
            # remove the randomly generated room code from user's session
            self.request.session.pop('room_code')
            host_id = self.request.session.session_key
            room_result = Room.objects.filter(host=host_id)

            if len(room_result) > 0:
                room = room_result[0]
                room.delete()

        return Response({'Message': 'Success'}, status=status.HTTP_200_OK)


class UpdateRoom(APIView):
    serializer_class = UpdateRoomSerializer

    def patch(self, request, format=None):
        # check if user in a session
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            code = serializer.data.get('code')

            queryset = Room.objects.filter(code=code)
            if not queryset.exists():
                return Response({'Message': 'Room does not exist'},
                                status=status.HTTP_404_NOT_FOUND)

            room = queryset.first()
            user_id = self.request.session.session_key
            if room.host != user_id:
                return Response(
                    {'Message': 'You are not the the host of this room'},
                    status=status.HTTP_403_FORBIDDEN)

            room.guest_can_pause = guest_can_pause
            room.votes_to_skip = votes_to_skip
            room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
            return Response(RoomSerializer(room).data,
                            status=status.HTTP_200_OK)

        return Response({'Bad Request': 'Invalid Data...'},
                        status=status.HTTP_400_BAD_REQUEST)
