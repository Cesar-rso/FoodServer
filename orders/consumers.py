from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Orders
from .serializers import OrderSerializer
from datetime import datetime


class OrdersConsumer(AsyncJsonWebsocketConsumer):


    async def connect(self):

        await self.accept()
        content = {"username": "system", "message": str(datetime.today().year) + "-" + str(datetime.today().month) + "-" + str(datetime.today().day)}
        await self.receive_json(content)


    async def receive_json(self, content):
        
        print("Receiving message...")
        date_msg = datetime.strptime(content['message'], '%Y-%m-%d')
        username = content['username']
        message = await get_Orders(date_msg)

        await self.send_json(
            {
                'type': 'websocket.send',
                'message': message,
                'username': username
            }
        )


@database_sync_to_async
def get_Orders(date: datetime) -> dict:

    orders = Orders.objects.filter(date__gt=date)
    if orders:
        message = OrderSerializer(orders).data
    else:
        message = {}

    return message