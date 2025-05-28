from typing import Any
from rest_framework import permissions, status
from django.shortcuts import render
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response 
from rest_framework.views import APIView
from .web3Score.web3Score import Web3TournamentScore
from web3 import Web3
import logging

logger = logging.getLogger(__name__)

class Web3Score(APIView):
    permission_classes = [permissions.AllowAny] #permissions.IsAuthenticatedOrReadOnly
    renderer_classes = [JSONRenderer]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.web3Score = Web3TournamentScore.getInstance()

    def get(self, request):
        try:
            id = request.query_params["id"]
        except:
            return Response(status.HTTP_400_BAD_REQUEST)
        return Response(self.web3Score.getTournamentScore(id))
        
    def post(self, request):
        try:
            id = request.data['id']
            score = request.data['score']
        except:
            return Response(status.HTTP_400_BAD_REQUEST)
        tx = self.web3Score.setTournamentScore(id, score)
        return Response({ "success": True, "tx": tx })