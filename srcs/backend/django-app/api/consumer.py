from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
from api.models import User
import sys
import logging
logger = logging.getLogger(__name__)

class UserConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.id:
            return await self.close()
        await self.accept("pong")
        self.user.online += 1
        await sync_to_async(self.user.save)()

    async def disconnect(self, close_code):
        if not self.user.is_authenticated:
            return
        if self.user.online:
            await sync_to_async(self.user.refresh_from_db)()
            self.user.online -= 1
            await sync_to_async(self.user.save)()

    async def receive_json(self, content):
        pass

def _start():
    if "backend.asgi:application" not in sys.argv:
        if "runserver" not in sys.argv:
                return
    try:
        onlineUser = User.objects.all().exclude(online=0)
        logger.warning(f"Setting {len(onlineUser)} user offline")
        for user in onlineUser:
            user.online = 0
            user.save()
    except:
        pass
_start()