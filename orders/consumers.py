from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import Orders
from datetime import datetime


class OrdersConsumer(AsyncJsonWebsocketConsumer):


    async def connect(self):

        await self.accept()


    async def receive_json(self, content):
        
        date_msg = datetime.strptime(content['message'], '%Y-%m-%d')
        username = content['username']
        message = Orders.objects.filter(date__gt=date_msg)

        await self.send_json(
            {
                'type': 'websocket.send',
                'message': message,
                'username': username
            }
        )

