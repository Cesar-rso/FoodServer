from typing import Any
import matplotlib.pyplot as plt
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic
from django.views.generic import CreateView, UpdateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from .serializers import *
from .models import *
import requests

# API endpoints

class Order(APIView):
    # REST API view where waiters handle orders. The waiter must be an authenticated user
    permission_classes = (IsAuthenticated,)
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
    # REST API view to handle suppliers
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

# Web pages (front-end)

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
    # View that lists all suppliers, allowing deletion and inclusion of new ones.
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
    
    def put(self, request):
        supplier = Suppliers.objects.get(pk=request.POST['id'])
        supplier.name = request.POST['name']
        supplier.address = request.POST['address']
        supplier.phone = request.POST['phone']
        supplier.supply_type = request.POST['supply_type']
        supplier.save()

        return redirect('suppliers')
    
    def delete(self, request):
        supplier = Suppliers.objects.get(pk=request.POST['submit'])
        supplier.delete()

        return redirect('suppliers')
    

class ListUsers(generic.ListView):
    # View that lists all users, allowing deletion and inclusion of new ones.
    template_name = "orders/users.html"
    context_object_name = "users"

    def get_queryset(self) -> QuerySet[Any]:
        return User.objects.all().order_by('username')
    
    def post(self, request):
        usr_id = request.POST['search']
        if usr_id.isdecimal():
            usr = User.objects.filter(pk=int(usr_id))
        else:
            usr = User.objects.filter(username=usr_id)
        context = {'users': usr}

        return render(request, 'orders/users.html', context)
    
    def delete(self, request):
        usr = User.objects.get(pk=request.POST['submit'])
        usr.delete()

        return redirect('users')


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


class SupplierUpdate(UpdateView):
    model = Suppliers
    fields = '__all__'
    template_name = "orders/supplier-update-form.html"


class ProductUpdate(UpdateView):
    model = Products
    fields = '__all__'
    template_name = "orders/product-update-form.html"


class UserUpdate(UpdateView):
    model = User
    fields = ['username', 'email']
    template_name = "orders/user-update-form.html"


def home(request):
    context = {}
    return render(request, "orders/index.html", context)


def new_order(request):
    # View for making new orders from the browser
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
    # View for saving payments and updating orders payment status
    if request.method == "POST":
        table = request.POST['pay']
        orders = Orders.objects.filter(table=table)
        payment = Payments.objects.create(user=request.user)
        payment.save()
        total = 0.0
        for order in orders:
            for product in order.product.all():
                total += product.price
            payment.order.add(order)
            order.status = "PA"
            order.save()
        payment.value = total
        payment.save()
        return redirect('checkout')
    

def reports(request):
    # View for generating graphs, like sales and expenses graphs
    context = {}
    context["plot"] = ""

    if request.method == "POST":
        rep_type = request.POST['rep_type']
        start_period = request.POST['start_period']
        end_period = request.POST['end_period']
        totals = {}
        labels = []

        if rep_type == "ME":
            expenses = Inputs.objects.filter(date__gte=start_period).filter(date__lte=end_period).order_by("date")

            for expense in expenses:
                e_key = expense.date.strftime("%B")

                if e_key in totals.keys():
                    totals[e_key] += expense.total
                else:
                    totals[e_key] += expense.total

            labels.append("Months ")
            labels.append("Total expenses")
            labels.append('plot_expenses_period' + str(start_period) + '.png')

        if rep_type == "MS":
            sales = Payments.objects.filter(date__gte=start_period).filter(date__lte=end_period).order_by("date")

            for sale in sales:
                s_key = sale.date.strftime("%B")

                if s_key in totals.keys():
                    totals[s_key] += sale.value
                else:
                    totals[s_key] = sale.value

            labels.append("Months ")
            labels.append("Total sales")
            labels.append('plot_sales_period' + str(start_period) + '.png')

        if rep_type == "SP":
            sales = Payments.objects.filter(date__gte=start_period).filter(date__lte=end_period).order_by("date")

            for sale in sales:
                for order in sale.order.all():
                    for product in order.product.all():

                        if product.name in totals.keys():
                            totals[product.name] += 1
                        else:
                            totals[product.name] = 1

            labels.append("Products ")
            labels.append("Total sales (quantity)")
            labels.append('plot_ProductSales_period' + str(start_period) + '.png')

    try:
        plt.bar(totals.keys(), totals.values())
        plt.xlabel(labels[0])
        plt.ylabel(labels[1])
        plt.savefig('./media/' + labels[2])

        context["plot"] = labels[2]
    except Exception as e:
        print(e)

    return render(request, "orders/reports.html", context)


def login_request(request):
    # Basic login method
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            u = User.objects.get(username=username)
        except:       
            context['message'] = "Invalid username."
            return render(request, 'orders/error.html', context)
            
        if not u.has_usable_password():
            context['message'] = "Define initial password."
            context['username'] = username
            return render(request, 'orders/newpass.html', context)
        
        else:
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:  # check if user account is not banned/blocked
                    login(request, user)
                    return redirect('home')
                
            context['message'] = "Invalid username or password."
            return render(request, 'orders/error.html', context)


def logout_request(request):
    # Basic logout method
    logout(request)
    return redirect('home')


def new_user(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'orders/newuser.html', context)
    
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']

        u = User.objects.create_user(username=username, email=email)
        u.save()

        return redirect('home')
    

def delete_user(request):
    context = {}
    print(request.method)
    if request.method == 'GET':
        usr = User.objects.all()
        context["users"] = usr

        return render(request, 'orders/deleteuser.html', context)
    
    if request.method == 'POST':
        usr = User.objects.get(pk=request.POST['user_id'])
        usr.delete()

        return redirect('home')


def update_password(request, pk):
    context = {}
    if request.method == "GET":
        usr = User.objects.get(pk=pk)
        context['username'] = usr.username
        return render(request, 'orders/newpass.html', context)
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        u = User.objects.get(username=username)
        u.set_password(password)
        u.save()

        context['message'] = "Password successfully set!"
        return render(request, 'orders/error.html', context)
    

def company_info(request):
    context = {}
    cmp = Company.objects.all()[0]
    if request.method == "GET":
        context["company"] = cmp 
        return render(request, 'orders/company_info.html', context)
    
    if request.method == "POST":
        cmp.name = request.POST['name']
        cmp.address = request.POST['address']
        cmp.phone = request.POST['phone']
        cmp.logo = request.POST['logo']

        cmp.save()

        return redirect('info')
    
