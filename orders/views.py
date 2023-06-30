from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic
from django.views.generic import CreateView
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from .serializers import OrderSerializer, ProductSerializer
from .models import Order, Products, Payments
import requests


class PlaceOrder(APIView):
    # REST API view where waiters place orders. The waiter must be an authenticated user
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser,)

    def post(self, request):
        data = request.data

        order = Order(table=data['table'], status=data['status'])
        order.save()
        products = data['products']
        #counter = 0
        stats = "Order placed!"
        for product in products:
            try:
                p1 = Products.objects.get(pk=products[product])
                order.product.add(p1)
                #counter += 1
            except Exception as e:
                stats = "Error! Could not find product!"
        resp = {"status": stats}

        return Response(resp)


class CheckOrder(APIView):
    # REST API view where waiters can check specific orders (status, products, etc)
    parser_classes = (JSONParser,)

    def get(self, request):
        data = request.GET
        order = Order.objects.filter(table=data['table']).order_by('date').first()
        serializer = OrderSerializer(order)

        if order is None:
            response = {"exception": "Couldn't find requested order!"}
        else:
            response = serializer.data

        return Response(response)


class CancelOrder(APIView):
    # REST API view for waiters to cancel orders. The waiter must be an authenticated user
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser,)

    def post(self, request):
        data = request.data

        try:
            order = Order.objects.filter(table=data['table']).order_by('date').first()
            if order is None:
                resp = {"exception": "Couldn't find requested product!"}
            else:
                order.status = Order.Status.CANCELED
                order.save()
                resp = {"status": "Order canceled!"}
        except ObjectDoesNotExist:
            resp = {"exception": "Couldn't find requested product!"}

        return Response(resp)


class CheckProduct(APIView):
    # REST API view where waiters can search for specific products
    parser_classes = (JSONParser,)

    def get(self, request):

        data = request.GET
        try:
            products = Products.objects.get(pk=int(data['id']))
            serializer = ProductSerializer(products)
            resp = serializer.data
        except ObjectDoesNotExist:
            resp = {"exception": "Couldn't find requested product!"}

        return Response(resp)


class ControlOrders(generic.ListView):
    # View that gives employees in the kitchen full control of the orders made by waiters
    template_name = 'orders/index.html'
    context_object_name = 'all_orders'

    def get_queryset(self):
        return Order.objects.all().order_by('date')

    def post(self, request):
        if 'submit' in request.POST.keys():
            order = Order.objects.get(pk=request.POST['submit'])
            order.status = request.POST['status']
            order.save()

        if 'delete' in request.POST.keys():
            order = Order.objects.get(pk=request.POST['delete'])
            order.delete()

        return redirect('orders')


class Checkout(generic.ListView):
    # View that allows payment of orders from specific table
    template_name = 'orders/checkout.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.all().order_by('date')

    def post(self, request):
        if 'search' in request.POST.keys() and request.POST['search'].isdecimal():
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
    # View that lists all products, allowing deletion and inclusion of new ones.
    # Unlike the REST API CheckProduct view, this one is meant for employees in the kitchen
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
    # Basic form view for adding new products to the system
    model = Products
    fields = '__all__'
    template_name = "orders/product-form.html"


def new_order(request):
    # Method for making new orders from the browser
    if request.method == "GET":
        products = Products.objects.all()
        context = {"products": products}
        return render(request, "orders/neworder.html", context)
    
    if request.method == "POST":
        table = request.POST['table_number']

        context = {'table': table, 'status':'WA', 'products': []}
        response = requests.post(request.build_absolute_uri(reverse('new-order')), json=context)
        data = response.json

        if data["status"] == "Pedido adicionado com sucesso!":
            return redirect('new_order')
        else:
            return render(request, "error.html", {"message": "Erro ao realizar pedido!"})


def pay_orders(request):
    # Method for saving payments and updating orders payment status
    if request.method == "POST":
        table = request.POST['pay']
        orders = Order.objects.filter(table=table)
        payment = Payments.objects.create(user=request.user)
        total = 0.0
        for order in orders:
            for product in order.product.all():
                total += product.price
            order.payment = payment
            order.status = "PA"
            order.save()
        payment.value = total
        payment.save()
        return redirect('checkout')


def login_request(request):
    # Basic login method
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
    # Basic logout method
    logout(request)
    return redirect('orders')
