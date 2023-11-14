from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Orders, Products
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
    prod_details = []
    if len(orders) > 0:
        message = OrderSerializer(orders[0]).data
        for item in message["product"]:
            product = Products.objects.get(pk=item)
            prod_details.append({"id": product.id, "name": product.name, "price": product.price})

        message["product"] = prod_details

    else:
        message = {}

    return message