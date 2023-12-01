from typing import Any
import matplotlib.pyplot as plt
from django.db.models.query import QuerySet
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
from rest_framework.authtoken.models import Token
from .serializers import *
from .models import *
import requests


class Order(APIView):
    # REST API view where waiters handle orders. The waiter must be an authenticated user
    # permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser,)

    def get(self, request):
        data = request.GET

        if data['table']:
            order = Orders.objects.filter(table=data['table']).order_by('date').first()
        else:
            order = Orders.objects.all()

        serializer = OrderSerializer(order)
        response = serializer.data

        return Response(response)

    def post(self, request):
        data = request.data

        order = Orders(table=data['table'], status=data['status'])
        order.save()
        products = data['products']
        
        stats = "Order placed!"
        for product in products:
            try:
                p1 = Products.objects.get(pk=products[product])
                order.product.add(p1)
                
            except Exception as e:
                stats = "Error! Could not find product!"
        order.save()
        resp = {"status": stats}

        return Response(resp)
    
    def put(self, request):
        data = request.data

        order = Orders.objects.get(pk=data['id'])
        order.table = data['table']
        order.status = data['status']
        order.save()
        
        products = data['products']
        
        stats = "Order updated!"
        for product in products:
            try:
                p1 = Products.objects.get(pk=products[product])
                order.product.add(p1)
                
            except Exception as e:
                stats = "Error! Could not find product!"
        order.save()
        resp = {"status": stats}

        return Response(resp)
    
    def delete(self, request):
        data = request.data

        try:
            order = Orders.objects.filter(table=data['table']).order_by('date').first()
            if order is None:
                resp = {"exception": "Couldn't find requested order!"}
            else:
                order.status = Orders.Status.CANCELED
                order.save()
                resp = {"status": "Order canceled!"}
        except ObjectDoesNotExist:
            resp = {"exception": "Couldn't find requested order!"}

        return Response(resp)


class Product(APIView):
    # REST API view to handle products
    parser_classes = (JSONParser,)

    def get(self, request):

        data = request.GET
        if data['id']:
            products = Products.objects.get(pk=int(data['id']))       
        else:
            products = Products.objects.all()

        serializer = ProductSerializer(products)
        resp = serializer.data

        return Response(resp)
    
    def post(self, request):
        data = request.data 

        product = Products(name = data['name'], description=data['description'], price=data['price'], cost=data['cost'], picture=data['picture'])
        product.save()
        supplier = Supplier.objects.get(id=data['supplier'])

        if supplier:
            product.supplier = supplier
            product.save()
        resp = {"status": "New product successfully registered!"}

        return Response(resp)
    
    def put(self, request):
        data = request.data 

        try:
            product = Products.objects.get(pk=data['id'])
            product.name = data['name']
            product.description = data['description']
            product.price = data['price']
            product.cost = data['cost']
            product.picture = data['picture']

            supplier = Supplier.objects.get(pk=data['supplier'])
            if supplier:
                product.supplier = supplier

            resp = {"status": "Product successfully updated!"}

        except Exception as e:
            resp = {"status": f"{e}"}

        return Response(resp)
    
    def delete(self, request):
        data = request.data 

        try:
            product = Products.objects.get(pk=data['id'])
            product.delete()
            resp = {"status": "Product successfully deleted!"}
        except Exception as e:
            resp = {"status": f"{e}"}

        return Response(resp)
    

class Supplier(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser,)

    def get(self, request):
        data = request.GET 

        if data['id']:
            suppliers = Suppliers.objects.get(pk=data['id'])
        else:
            suppliers = Suppliers.objects.all()

        serializer = SupplierSerializer(suppliers)
        response = serializer.data

        return Response(response)
    
    def post(self, request):
        data = request.data 

        supplier = Suppliers(name=data['name'], address=data['address'], phone=data['phone'], supply_type=data['supply_type'])
        supplier.save()

        resp = {"status": "New supplier successfully registered!"}

        return Response(resp)
    
    def put(self, request):
        data = request.data 

        supplier = Suppliers.objects.get(pk=data['id'])
        supplier.name = data['name']
        supplier.address = data['address']
        supplier.phone = data['phone']
        supplier.supply_type = data['supply_type']
        supplier.save()

        resp = {"status": "Supplier successfully updated!"}
        return Response(resp)
    
    def delete(self, request):
        data = request.data 

        try:
            supplier = Suppliers.objects.get(pk=data['id'])
            supplier.delete()
            resp = {"status": "Supplier deleted!"}
        except Exception as e:
            resp = {"status": f"{e}"}

        return Response(resp)


class ControlOrders(generic.ListView):
    # View that gives employees in the kitchen full control of the orders made by waiters
    template_name = 'orders/orders.html'
    context_object_name = 'all_orders'

    def get_queryset(self):
        return Orders.objects.all().order_by('date')

    def post(self, request):
        if 'submit' in request.POST.keys():
            order = Orders.objects.get(pk=request.POST['submit'])
            order.status = request.POST['status']
            order.save()

        return redirect('orders')
    
    def delete(self, request):
        order = Orders.objects.get(pk=request.POST['delete'])
        order.delete()

        return redirect('orders')


class Checkout(generic.ListView):
    # View that allows payment of orders from specific table
    template_name = 'orders/checkout.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Orders.objects.all().order_by('date')

    def post(self, request):
        if 'search' in request.POST.keys() and request.POST['search'].isdecimal():
            table = request.POST['search']
            orders = Orders.objects.filter(table=table)
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
        
    def delete(self, request):
        product = Products.objects.get(pk=request.POST['submit'])
        product.delete()

        return redirect('products')
    

class ListSuppliers(generic.ListView):
    template_name = "orders/suppliers.html"
    context_object_name = "suppliers"

    def get_queryset(self) -> QuerySet[Any]:
        return Suppliers.objects.all().order_by('name')
    
    def post(self, request):
        supp_id = request.POST['search']
        if supp_id.isdecimal():
            supplier = Suppliers.objects.filter(pk=int(supp_id))
        else:
            supplier = Suppliers.objects.filter(name=supp_id)
        context = {'suppliers': supplier}

        return render(request, 'order/suppliers.html', context)
    
    def delete(self, request):
        supplier = Suppliers.objects.get(pk=request.POST['submit'])
        supplier.delete()

        return redirect('suppliers')


class ProductRegistration(CreateView):
    # Basic form view for adding new products to the system
    model = Products
    fields = '__all__'
    template_name = "orders/product-form.html"


class SupplierRegistration(CreateView):
    # Basic form view for adding new suppliers to the system
    model = Suppliers
    fields = '__all__'
    template_name = "orders/supplier-form.html"


def home(request):
    context = {}
    return render(request, "orders/index.html", context)


def new_order(request):
    # Method for making new orders from the browser
    if request.method == "GET":
        products = Products.objects.all()
        context = {"products": products}
        return render(request, "orders/neworder.html", context)
    
    if request.method == "POST":
        table = request.POST['table_number']

        context = {'table': table, 'status':'WA', 'products': []}
        token = Token.objects.get_or_create(user=request.user)
        t_header = {"Authorization": f'Token {token[0].key}', "Content-Type": "application/json"}
        response = requests.post(request.build_absolute_uri(reverse('api-orders')), data=context, headers=t_header)
        data = response.json()
        print(data)

        if data["status"] == "Pedido adicionado com sucesso!":
            return redirect('orders')
        else:
            return render(request, "error.html", {"message": "Erro ao realizar pedido!"})


def pay_orders(request):
    # Method for saving payments and updating orders payment status
    if request.method == "POST":
        table = request.POST['pay']
        orders = Orders.objects.filter(table=table)
        payment = Payments.objects.create(user=request.user)
        total = 0.0
        for order in orders:
            for product in order.product.all():
                total += product.price
            payment.order = order
            order.status = "PA"
            order.save()
        payment.value = total
        payment.save()
        return redirect('checkout')
    

def reports(request):
    context = {}
    context["plot"] = ""

    if request.method == "POST":
        rep_type = request.POST['rep_type']
        start_period = request.POST['start_period']
        end_period = request.POST['end_period']

        if rep_type == "ME":
            expenses = Inputs.objects.filter(date__gte=start_period).filter(date__lte=end_period).order_by("date")
            totals = {}

            for expense in expenses:
                e_key = expense.date.month

                if e_key in totals.keys():
                    totals[e_key] += expense.total
                else:
                    totals[e_key] += expense.total

            plt.bar(totals.keys(), totals.values())
            plt.xlabel("Months ")
            plt.ylabel("Total expenses")

            file = 'plot_expenses_period' + str(start_period) + '.png'
            plt.savefig('./media/' + file)

            context["plot"] = file

        if rep_type == "MS":
            sales = Payments.objects.filter(date__gte=start_period).filter(date__lte=end_period).order_by("date")
            totals = {}

            for sale in sales:
                s_key = sale.date.month

                if s_key in totals.keys():
                    totals[s_key] += sale.value
                else:
                    totals[s_key] = sale.value

            plt.bar(totals.keys(), totals.values())
            plt.xlabel("Months ")
            plt.ylabel("Total sales")

            file = 'plot_sales_period' + str(start_period) + '.png'
            plt.savefig('./media/' + file)

            context["plot"] = file


    return render(request, "orders/reports.html", context)


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
                return redirect('home')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'orders/error.html', context)


def logout_request(request):
    # Basic logout method
    logout(request)
    return redirect('home')
