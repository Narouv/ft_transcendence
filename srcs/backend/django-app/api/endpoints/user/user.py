from django.contrib.auth import password_validation
from rest_framework import permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response 
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from api.models import User
import logging

logger = logging.getLogger(__name__)

class UserManager(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [JSONRenderer]

    def post(self, request):
        try:
            username = request.data['username']
            password = request.data['password']
            email = request.data['email']
        except:
            return Response(status.HTTP_400_BAD_REQUEST)
        if len(username) < 3:
            return Response({'success': False, "error": "Username invalid min. 3 character"})
        if len(username) > 25:
            return Response({'success': False, "error": "Username invalid max. 25 character"})
        if not username.isalnum():
            return Response({'success': False, "error": "Username invalid only aA-zZ 0-9 allowed"})
        if (len(email) < 5) or '@' not in email or '.' not in email:
            return Response({'success': False, "error": "Email invalid"})
        if User.objects.filter(username=username).exists():
            return Response({'success': False, "error": "Username already in use"})
        if User.objects.filter(email=email).exists():
            return Response({'success': False, "error": "Email already in use"})
        try:
            password_validation.validate_password(password)
        except  ValidationError as error:
            if len(error.messages):
                return Response({'success': False, "error": error.messages[1] if len(error.messages) > 1 else error.messages[0]})
            return Response({'success': False, "error": "Password not secure!"})
        user = User.objects.create_user(username, email, password)
        if user is None:
            return Response({'success': False})
        return Response({'success': True})

    def patch(self, request):
        if not request.user.is_authenticated:
            return Response(status.HTTP_401_UNAUTHORIZED)
        try:
            playerName = request.data['playerName']
        except:
            return Response(status.HTTP_400_BAD_REQUEST)
        if len(playerName) < 3:
            return Response({'success': False, "error": "Player Name invalid min. 3 character"})
        if len(playerName) > 20:
            return Response({'success': False, "error": "Player Name invalid max. 20 character"})
        if not playerName.isalnum():
            return Response({'success': False, "error": "Player Name invalid only aA-zZ 0-9 allowed"})
        if User.objects.filter(nickname=playerName).exclude(pk=request.user.id).exists():
            return Response({'success': False, "error": "Player Name already in use"})
        request.user.nickname = playerName
        request.user.save()
        return Response({'success': True})
    
class PasswordReset(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def post(self, request):
        try:
            newPassword = request.data['password']
        except:
            return Response(status.HTTP_400_BAD_REQUEST)
        try:
            password_validation.validate_password(newPassword)
        except  ValidationError as error:
            if len(error.messages):
                return Response({'success': False, "error": error.messages[1] if len(error.messages) > 1 else error.messages[0]})
            return Response({'success': False, "error": "Password not secure!"})
        user = User.objects.get(pk=request.user.id)
        user.set_password(newPassword)
        user.save()
        return Response({'success': True})
        