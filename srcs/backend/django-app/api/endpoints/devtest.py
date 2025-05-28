from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.utils.http import urlencode
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import serializers, permissions, viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from tpong.models import PongMatch, PongStats
from tpong.game.networking.lobby.PongLobbyManager import lobbyManagerInstance
from api.models import User
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.contrib.auth import authenticate, login
from rest_framework import authentication, permissions
import logging
logger = logging.getLogger(__name__)
# Create your views here.

class LobbyEdit(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]
    def get(self, request, type):
        return Response({ 'msg': f'Active match { PongMatch.getActiveMatch(request.user) }' })
    
    def post(self, request, type):
        if type == 'local':
            lobby = lobbyManagerInstance.createLobby()
            lobbyManagerInstance.registerUserToLobby(lobby, request.user)
            return Response({ 
                'success': True,
                'lobbyUUID': lobby.uuid,
                })
        #if type == 'pvp':
        #    username = request.data['username']
        #    enemyUser = User.objects.get(username=username)
        #    match = PongMatch(type=PongMatch.PVP_GAME, mode=PongMatch.CLASSIC)
        #    match.status = PongMatch.ACTIVE
        #    match.save()
        #    match.addPlayer(request.user)
        #    match.addPlayer(enemyUser)
        #    lobby = lobbyManagerInstance.createLobby(match)
        #    return Response({ 
        #        'success': True,
        #        'lobbyUUID': lobby.uuid,
        #        })
        return Response({ 
            'sucess': False,
            'msg': f'Invalid match type: { type }!'
            })

@api_view(['GET', 'POST'])
@csrf_exempt
def testView(request):
    logger.warning(f"User {request.user}")
    return HttpResponse("{}")

@csrf_exempt
def loginPage(request, username, password):
    user = authenticate(username=username, password=password)
    if user is None:
        return JsonResponse({'success': False})
    refresh_token = RefreshToken.for_user(user)
    access = str(refresh_token.access_token)
    response = JsonResponse({'access': access, 'refresh': str(refresh_token)})
    response.set_cookie('jwt_token', access, expires=refresh_token.access_token.payload['exp'], httponly=True)
    return response

def register(request, username, email, password):
    user = User.objects.create_user(username, email, password)
    if user is None:
        return JsonResponse({'success': False})
    return JsonResponse({'success': True})

class MatchSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PongMatch
        fields = ['type', 'mode', 'status', 'stats']


class MatchViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = PongMatch.objects.all().order_by('status')
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]

