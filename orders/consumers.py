from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Orders
from .serializers import OrderSerializer
from datetime import datetime


class OrdersConsumer(AsyncJsonWebsocketConsumer):


    async def connect(self):

        await self.accept()
        current_time = str(datetime.today().year) + "-" + str(datetime.today().month) + "-" + str(datetime.today().day) + " " + str(datetime.today().hour) + ":" + str(datetime.today().minute)
        content = {"username": "system", "message": current_time}
        await self.receive_json(content)


    async def receive_json(self, content):
        
        date_msg = datetime.strptime(content['message'], '%Y-%m-%d %H:%M')
        username = content['username']
        try:
            message = await get_Orders(date_msg)
        except:
            message = await get_Orders(datetime.now())

        await self.send_json(
            {
                'type': 'websocket.send',
                'message': message,
                'username': username
            }
        )


@database_sync_to_async
def get_Orders(date: datetime) -> dict:

    orders = Orders.objects.filter(date__gt=date).order_by("date")
    if len(orders) > 0:
        message = OrderSerializer(orders[0]).data
    else:
        message = {}
        print("No new orders!")

    return message