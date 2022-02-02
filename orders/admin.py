from django.contrib import admin
from .models import Products, Order, Waiters, Payments

# Register your models here.
admin.site.register(Products)
admin.site.register(Order)
admin.site.register(Waiters)
admin.site.register(Payments)
