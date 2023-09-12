from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Order
from django.contrib.auth.models import User
from datetime import datetime
import json


class OrdersConsumer(AsyncWebsocketConsumer):

    # def __init__(self):
    #     self.room_name = ''
    #     self.room_group_name = ''

    async def connect(self):

        current_date = str(datetime.today().year) + str(datetime.today().month) + str(datetime.today().day)
        self.room_name = 'orders' #self.scope['url_route']
        self.room_group_name = current_date + '_' + self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # message = text_data_json['message']
        username = text_data_json['username']
        message = Order.objects.filter(date__gt=text_data_json['message'])

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'room_message',
                'message': message,
                'username': username
            }
        )

    async def room_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

