from rest_framework import permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from api.TwoFacAuth import TwoFacAuth
import logging

logger = logging.getLogger(__name__)

class Login(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [JSONRenderer]

    def post(self, request):
        try:
            username = request.data['username']
            password = request.data['password']
        except:
            return Response(status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({
                'success': False,
                "error": "Invalid credentials!"
                })
        if not TwoFacAuth.verifyRequest(user, request.data.get('code')):
            return Response({
                'success': False,
                "error": "Invalid 2FA code!"
                })
        token = RefreshToken.for_user(user)
        access = token.access_token
        response = Response({
            'success': True,
            'data': {
                'access': str(access),
                'refresh': str(token),
                'expiry': access.payload['exp']
        }})
        return response
