from django.db import models
from django.utils.translation import gettext_lazy as _
import datetime
from django.conf import settings
from django.urls import reverse
from consumers import OrdersConsumer


class Supplier(models.Model):

    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    phone = models.IntegerField()
    supply_type = models.CharField(max_length=200)


class Payments(models.Model):

    class PayType(models.TextChoices):
        CASH = 'CA', _('Cash')
        DEBIT = 'DE', _('Debit Card')
        CREDIT = 'CR', _('Credit Card')

    value = models.FloatField(default=0.0)
    date = models.DateTimeField(default=datetime.datetime.now)
    method = models.CharField(max_length=100, choices=PayType.choices, default=PayType.CASH)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
    )


class Products(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=700)
    price = models.FloatField(default=0.0)
    cost = models.FloatField(default=0.0)
    picture = models.ImageField(upload_to='products/', default='default.jpg')
    supplier = models.ForeignKey(Supplier, on_delete=models.DO_NOTHING)

    def get_absolute_url(self):
        return reverse('products')


class Inputs(models.Model):
    products = models.ManyToManyField(Products, on_delete=models.DO_NOTHING)
    supplier = models.ForeignKey(Supplier, on_delete=models.DO_NOTHING)
    discount = models.IntegerField(default=0)
    total = models.FloatField(default=0.0)

    def save(self, *args, **kwargs):
        # Implementear calculo de valor total com desconto
        super.save(*args, **kwargs)


class Order(models.Model):

    class Status(models.TextChoices):
        WAITING = 'WA', _('Waiting')
        DELIVERED = 'DE', _('Delivered')
        PARTIAL_DELIVER = 'PD', _('Partially Delivered')
        PREPARING = 'PP', _('Preparing')
        CANCELED = 'CA', _('Canceled')
        PAID = 'PA', _('Paid')

    product = models.ManyToManyField(Products)
    table = models.IntegerField(default=1)
    status = models.CharField(max_length=100, choices=Status.choices, default=Status.WAITING)
    date = models.DateTimeField(default=datetime.datetime.now)
    payment = models.ForeignKey(Payments, on_delete=models.DO_NOTHING, default=1)

    def save(self, *args, **kwargs):
        # Implementear resposta para atualização async
        socket = OrdersConsumer()
        socket.connect()
        data = {'message': {'product': self.product, 'table': self.table, 'status': self.status, 'date': self.date, 'payment': self.payment}, 'username': 'system'}
        socket.receive(data)
        socket.disconnect()
        super.save(*args, **kwargs)


class Waiters(models.Model):
    name = models.CharField(max_length=200)
    admission = models.DateField(default=datetime.date.today)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )



