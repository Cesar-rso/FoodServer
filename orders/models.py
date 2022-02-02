from django.db import models
from django.utils.translation import gettext_lazy as _
import datetime
from django.conf import settings
from django.urls import reverse


class Payments(models.Model):

    value = models.FloatField(default=0.0)
    date = models.DateTimeField(default=datetime.datetime.now)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
    )


class Products(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=700)
    price = models.FloatField(default=0.0)
    picture = models.ImageField(upload_to='products/', default='default.jpg')

    def get_absolute_url(self):
        return reverse('products')


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


class Waiters(models.Model):
    name = models.CharField(max_length=200)
    admission = models.DateField(default=datetime.date.today)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )



