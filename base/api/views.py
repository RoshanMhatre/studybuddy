from base.models import Room
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import RoomSerializer


@api_view(['GET'])
def getRoutes(request):
    """
    GET API returns the information about the other APIs available

    Receives:
      request: request from the user

    Returns:
      response: drf response stating the info about APIs
    """
    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms/:id'
    ]
    return Response(routes)


@api_view(['GET'])
def getRooms(request):
    """
    GET API returns all the rooms present in the DB

    Receives:
      request: request from the user

    Returns:
      response: serialized data containing info about all rooms
    """
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getRoom(request, pk: str):
    """
    GET API returns a specific room requested

    Receives:
      request: request from the user

    Returns:
      response: serialized data containing info about the room
    """
    room = Room.objects.get(id=pk)
    serializer = RoomSerializer(room, many=False)
    return Response(serializer.data)