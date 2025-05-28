from rest_framework import permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response 
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)

class Logout(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [JSONRenderer]

    def post(self, request):
        try:
            refreshToken = request.data['refresh']
            token = RefreshToken(refreshToken)
            token.blacklist()
        except: 
            return Response({}, status.HTTP_400_BAD_REQUEST)
        response = Response({ 'success': True })
        return response
