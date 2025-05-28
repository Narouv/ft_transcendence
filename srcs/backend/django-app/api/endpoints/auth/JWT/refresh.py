from rest_framework import permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response 
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)

class TokenRefresh(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [JSONRenderer]

    def post(self, request):
        try:
            refreshToken = request.data['refresh']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(token=refreshToken)
            access = token.access_token
        except:
            return Response({ "success": False })
        response = Response({ 
        'success': True,
        'data': {
            'access': str(access),
            'refresh': str(token),
            'expiry': access.payload['exp']
        }})
        return response
    
