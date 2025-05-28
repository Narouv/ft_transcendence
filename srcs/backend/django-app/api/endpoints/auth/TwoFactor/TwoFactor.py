from rest_framework import permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from tpong.game.networking.lobby import PongLobbyManager
from api.TwoFacAuth import TwoFacAuth
import logging

logger = logging.getLogger(__name__)

class TwoFactorAPI(APIView):
	permission_classes = [permissions.IsAuthenticated]
	renderer_classes = [JSONRenderer]

	def get(self, request):
		uri = TwoFacAuth.generate2FA(request.user)
		if uri:
			return Response({'success': True, 'data': uri})
		return Response({'success': False, 'error': '2FA already enabled'})

	def post(self, request):
		code = request.data.get('code')
		if TwoFacAuth.verify2FA(request.user, code):
			return Response({'success': True, 'msg': '2FA successfully verified'})
		return Response({'success': False, 'error': '2FA verification failed'})

	def delete(self, request):
		password = request.data.get('password')
		if TwoFacAuth.disable2FA(request.user, password):
			return Response({'success': True, 'msg': '2FA successfully disabled'})
		return Response({'success': False, 'error': '2FA disabling failed'})

	def put(self, request):
		password = request.data.get('password')
		uri = TwoFacAuth.reconfigure2FA(request.user, password)
		if uri:
			return Response({'success': True, 'data': uri, 'msg': 'reconfiguring 2FA'})
		return Response({'success': False, 'error': '2FA reconfiguration failed'})
