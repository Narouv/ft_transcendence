from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from asgiref.sync import sync_to_async
import logging
logger = logging.getLogger(__name__)

class ChannelsJWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def validateToken(self, token, scope):
        jwtAuth = JWTAuthentication()
        validated_token = jwtAuth.get_validated_token(raw_token=token.encode('utf-8'))
        if not validated_token:
            return False
        user = await sync_to_async(jwtAuth.get_user)(validated_token)
        if not user:
            return False
        scope['user'] = user
        return True

    async def authenticate(self, scope):
        headers = [header for header in scope['headers'] if header[0] == b'sec-websocket-protocol']
        protocols = headers[0][1].decode().split(', ')
        for protocol in protocols:
            if "Bearer____" not in protocol:
                continue
            type, token = protocol.split('____')
            try:
                if type == 'Bearer' and await self.validateToken(token, scope):
                    return True
            except:
                return False
        return False
        
    async def __call__(self, scope, receive, send):
        try:
            if not await self.authenticate(scope):
                scope['user'] = AnonymousUser()
        except:
            scope['user'] = AnonymousUser()
        return await self.app(scope, receive, send)