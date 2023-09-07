from django.db import models
from django.utils.translation import gettext_lazy as _
import datetime
from django.conf import settings
from django.urls import reverse
# from .consumers import OrdersConsumer


class Suppliers(models.Model):

    name = models.CharField(max_length=200, default='')
    address = models.CharField(max_length=200, default='')
    phone = models.IntegerField(default=00000000)
    supply_type = models.CharField(max_length=200, default='')


class Products(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=700)
    price = models.FloatField(default=0.0)
    cost = models.FloatField(default=0.0)
    picture = models.ImageField(upload_to='products/', default='default.jpg')
    supplier = models.ForeignKey(Suppliers, on_delete=models.SET_NULL, default=0, null=True)

    def get_absolute_url(self):
        return reverse('products')


class Inputs(models.Model):
    products = models.ManyToManyField(Products)
    supplier = models.ForeignKey(Suppliers, on_delete=models.SET_NULL, null=True)
    discount = models.IntegerField(default=0)
    total = models.FloatField(default=0.0)

    def save(self, *args, **kwargs):
        # Implementear calculo de valor total com desconto
        sub_total = 0
        for product in self.products:
            sub_total += product.cost

        self.total = sub_total - (sub_total * (self.discount / 100))
        super.save(*args, **kwargs)


class Orders(models.Model):

    class Status(models.TextChoices):
        WAITING = 'WA', _('Waiting')
        DELIVERED = 'DE', _('Delivered')
        PARTIAL_DELIVER = 'PD', _('Partially Delivered')
        PREPARING = 'PP', _('Preparing')
        CANCELED = 'CA', _('Canceled')
        PAID = 'PA', _('Paid')

    product = models.ManyToManyField(Products, null=True)
    table = models.IntegerField(default=1)
    status = models.CharField(max_length=100, choices=Status.choices, default=Status.WAITING)
    date = models.DateTimeField(auto_now_add=True)

    '''def save(self, *args, **kwargs):
        # Implementear resposta para atualização async
        try:
            socket = OrdersConsumer()
            socket.connect()
            data = {'message': {'product': self.product, 'table': self.table, 'status': self.status, 'date': self.date, 'payment': self.payment}, 'username': 'system'}
            socket.receive(data)
            socket.disconnect()
        except:
            print("Async socket failed!")
        super.save(*args, **kwargs)'''
    
class Payments(models.Model):

    class PayType(models.TextChoices):
        CASH = 'CA', _('Cash')
        DEBIT = 'DE', _('Debit Card')
        CREDIT = 'CR', _('Credit Card')

    value = models.FloatField(default=0.0)
    date = models.DateTimeField(default=datetime.datetime.now)
    method = models.CharField(max_length=100, choices=PayType.choices, default=PayType.CASH)
    order = models.ManyToManyField(Orders)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )


class Waiters(models.Model):
    name = models.CharField(max_length=200)
    admission = models.DateField(default=datetime.date.today)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )



