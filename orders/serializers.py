from rest_framework import serializers
from .models import *


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Products
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    products = ProductSerializer(read_only=True, many=True)

    class Meta:
        model = Orders
        fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Suppliers
        fields = '__all__'