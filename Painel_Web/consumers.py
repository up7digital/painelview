from channels.generic.websocket import AsyncWebsocketConsumer
import json

class PainelConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("painel_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("painel_group", self.channel_name)

    async def receive(self, text_data):
        pass

    async def painel_update(self, event):
        await self.send(text_data=json.dumps({
            "action": "update"
        }))
