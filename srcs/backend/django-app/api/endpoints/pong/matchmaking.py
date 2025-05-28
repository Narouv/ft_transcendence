from rest_framework import permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response 
from rest_framework.views import APIView
from tpong.game.networking.lobby import PongLobbyManager
import logging

logger = logging.getLogger(__name__)

class Matchmaking(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get(self, request):
        type = request.data.get("type")
        lobby = PongLobbyManager.lobbyManagerInstance.getLobbyFromUser(request.user, type)
        if not lobby:
            return Response({"success": False})
        return Response({"success": True, 'data': {'lobbyUUID': lobby.uuid, 'type': lobby.type}})

    def post(self, request):
        try:
            type = request.data["type"]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        lobby = PongLobbyManager.lobbyManagerInstance.enterUserMatchmaking(request.user, type)
        if not lobby:
            return Response({"success": False})
        return Response({"success": True, 'data': {'lobbyUUID': lobby.uuid}})
    
    def delete(self, request):
        result = PongLobbyManager.lobbyManagerInstance.userLobbyLeave(request.user)
        return Response({"success": result})