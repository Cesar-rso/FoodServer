from django.shortcuts import render, redirect
from django.views import generic
from django.views.generic import CreateView, UpdateView
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from .serializers import OrderSerializer, ProductSerializer
from .models import Order, Products, Payments


class PlaceOrder(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = JSONParser().parse(request)

        order = Order(table=data['table'], status=data['status'])
        order.save()
        products = data['products']
        counter = 1
        for product in products:
            p1 = Products.objects.get(pk=products[product])
            order.product.add(p1)
            counter += 1
        resp = {"status": "Order placed!"}

        return Response(resp)


class CheckOrder(APIView):

    def get(self, request):
        data = JSONParser().parse(request)
        order = Order.objects.filter(table=data['table']).order_by('date')[0]
        serializer = OrderSerializer(order)

        return Response(serializer.data)


class CancelOrder(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = JSONParser().parse(request)
        order = Order.objects.filter(table=data['table']).order_by('date')[0]
        order.status = Order.Status.CANCELED
        order.save()
        resp = {"status": "Order canceled!"}

        return Response(resp)


class CheckProduct(APIView):

    def get(self, request):
        data = JSONParser().parse(request)
        products = Products.objects.get(pk=data['id'])

        serializer = ProductSerializer(products)

        return Response(serializer.data)


class ControlOrders(generic.ListView):
    template_name = 'orders/index.html'
    context_object_name = 'all_orders'

    def get_queryset(self):
        return Order.objects.all().order_by('date')

    def post(self, request):
        order = Order.objects.get(pk=request.POST['submit'])
        order.status = request.POST['status']
        order.save()

        return redirect('orders')

    def delete(self, request):
        order = Order.objects.get(pk=request.POST['submit'])
        order.delete()

        return redirect('orders')


class Checkout(generic.ListView):
    template_name = 'orders/checkout.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.all().order_by('date')

    def post(self, request):
        if 'search' in request.POST.keys() and request.POST['search'] != '':
            table = request.POST['search']
            orders = Order.objects.filter(table=table)
            total = 0.0
            for order in orders:
                if order.status != "PA":
                    for product in order.product.all():
                        total = total + product.price
            return render(request, 'orders/checkout.html', {'orders': orders, 'orders_total': total, 'table': table})
        else:
            return redirect('orders')


class ListProducts (generic.ListView):
    template_name = "orders/products.html"
    context_object_name = "products"

    def get_queryset(self):
        return Products.objects.all().order_by('name')

    def post(self, request):
        if 'search' in request.POST.keys() and request.POST['search'] != '':
            prod_id = request.POST['search']
            if prod_id.isdecimal():
                product = Products.objects.filter(pk=int(prod_id))
            else:
                product = Products.objects.filter(name=prod_id)
            context = {'products': product}

            return render(request, 'orders/products.html', context)

        if 'submit' in request.POST.keys() and request.POST['submit'] != '':
            product = Products.objects.get(pk=request.POST['submit'])
            product.delete()

            return redirect('products')


class ProductRegistration(CreateView):
    model = Products
    fields = '__all__'
    template_name = "orders/product-form.html"


def pay_orders(request):
    if request.method == "POST":
        table = request.POST['pay']
        orders = Order.objects.filter(table=table)
        payment = Payments.objects.create_payments(user=request.user)
        total = 0.0
        for order in orders:
            for product in order.product.all():
                total += product.price
            order.payment = payment.pk
            order.status = "PA"
            order.save()
        payment.value = total
        payment.save()
        return redirect('checkout')


def login_request(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:  # check if user account is not banned/blocked
                login(request, user)
                return redirect('orders')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'orders/error.html', context)


def logout_request(request):
    logout(request)
    return redirect('orders')
