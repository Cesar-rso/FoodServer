from typing import Any
import matplotlib.pyplot as plt
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.utils import translation
from django.conf import settings
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
from datetime import datetime
from .serializers import *
from .models import *
import requests
import json
import os

# API endpoints

class Order(APIView):
    # REST API view where waiters handle orders. The waiter must be an authenticated user
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser,)

    def get(self, request):
        data = request.GET

        if 'table' in data.keys():
            order = Orders.objects.filter(table=data['table']).order_by('date').first()
        else:
            order = Orders.objects.all()

        if not order:
            response = {"exception": "Couldn't find requested order!"}
            status = 404
        
        else:
            status = 200
            serializer = OrderSerializer(order)
            response = serializer.data

        return Response(response, status)

    def post(self, request):
        data = request.data

        order = Orders(table=data['table'], status=data['status'])
        order.save()
        products = data['products']
        
        status = 200
        for product in products:
            try:
                p1 = Products.objects.get(pk=products[product])
                order.product.add(p1)
                
            except Exception:
                resp = {"status": "Error! Could not find product!"}
                status = 404
                return Response(resp, status)
            
        order.save()
        resp = {"status": "Order placed!"}

        return Response(resp, status)
    
    def put(self, request):
        data = request.data
        status = 200

        order = Orders.objects.get(pk=data['id'])
        order.table = data['table']
        order.status = data['status']
        order.save()

        order.product.clear()
        
        products = data['products']
        
        for product in products:
            try:
                p1 = Products.objects.get(pk=products[product])
                order.product.add(p1)
                
            except Exception:
                status = 404
                resp = {"status": "Error! Could not find product!"}
                return Response(resp, status)
            
        order.save()
        resp = {"status": "Order updated!"}

        return Response(resp, status)
    
    def delete(self, request):
        data = request.data

        try:
            order = Orders.objects.filter(table=data['table']).order_by('date').first()
            if order is None:
                resp = {"exception": "Couldn't find requested order!"}
                status = 404
            else:
                order.status = Orders.Status.CANCELED
                order.save()
                resp = {"status": "Order canceled!"}
                status = 200
        except ObjectDoesNotExist:
            resp = {"exception": "Couldn't find requested order!"}
            status = 404

        return Response(resp, status)


class Product(APIView):
    # REST API view to handle products
    parser_classes = (JSONParser,)

    def get(self, request):

        data = request.GET
        if 'id' in data.keys():
            try:
                products = Products.objects.get(pk=int(data['id']))
            except:
                resp = {"exception": "Couldn't find requested product!"}
                return Response(resp, status=404)      
        else:
            products = Products.objects.all()

        serializer = ProductSerializer(products)
        resp = serializer.data

        return Response(resp)
    
    def post(self, request):
        data = request.data 

        product = Products(name = data['name'], description=data['description'], price=data['price'], cost=data['cost'], picture=data['picture'])
        product.save()
        supplier = Suppliers.objects.get(id=data['supplier'])

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

            supplier = Suppliers.objects.get(pk=data['supplier'])
            if supplier:
                product.supplier = supplier

            product.save()

            resp = {"status": "Product successfully updated!"}
            status = 200

        except Exception as e:
            resp = {"status": f"{e}"}
            status = 404

        return Response(resp, status)
    
    def delete(self, request):
        data = request.data 

        try:
            product = Products.objects.get(pk=data['id'])
            product.delete()
            resp = {"status": "Product successfully deleted!"}
            status = 200
        except Exception as e:
            resp = {"status": f"{e}"}
            status = 404

        return Response(resp, status)
    

class Supplier(APIView):
    # REST API view to handle suppliers
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser,)

    def get(self, request):
        data = request.GET 

        if 'id' in data.keys():
            try:
                suppliers = Suppliers.objects.get(pk=data['id'])
            except:
                resp = {"exception": "Couldn't find requested supplier!"}
                status = 404
                return Response(resp, status)
        else:
            suppliers = Suppliers.objects.all()

        serializer = SupplierSerializer(suppliers)
        response = serializer.data

        return Response(response)
    
    def post(self, request):
        data = request.data
        status = 200 

        try:
            supplier = Suppliers(name=data['name'], address=data['address'], phone=data['phone'], supply_type=data['supply_type'])
            supplier.save()

            resp = {"status": "New supplier successfully registered!"}
        except:
            status = 500
            resp = {"status": "Error saving supplier data!"}

        return Response(resp, status)
    
    def put(self, request):
        data = request.data 

        try:
            supplier = Suppliers.objects.get(pk=data['id'])
            supplier.name = data['name']
            supplier.address = data['address']
            supplier.phone = data['phone']
            supplier.supply_type = data['supply_type']
            supplier.save()

            status = 200
            resp = {"status": "Supplier successfully updated!"}
        except:
            status = 404
            resp = {"status": "Supplier not found!"}

        return Response(resp, status)
    
    def delete(self, request):
        data = request.data 

        try:
            supplier = Suppliers.objects.get(pk=data['id'])
            supplier.delete()
            status = 200
            resp = {"status": "Supplier deleted!"}
        except Exception as e:
            status = 404
            resp = {"status": f"{e}"}

        return Response(resp, status)
    

class Input(APIView):
    # REST API view to handle inputs (buys from suppliers)
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser,)

    def get(self, request):
        data = request.GET

        try:
            if 'supplier' in data.keys():
                supp = Suppliers.objects.get(pk=data["supplier"])
                inputs = Inputs.objects.get(supplier=supp)

            elif 'id' in data.keys():
                inputs = Inputs.objects.get(id=data["id"])

            elif 'date' in data.keys():
                inputs = Inputs.objects.get(date__date=datetime.datetime.strptime(data["date"], "%Y-%m-%dT%H:%M"))

            else:
                inputs = Inputs.objects.all()

            status = 200
            serializer = InputSerializer(inputs)
            resp = serializer.data

        except:
            resp = {"exception": "Couldn't find requested order!"}
            status = 404
        
        return Response(resp, status)

    def post(self, request):
        data = request.data 

        try:
            supp = Suppliers.objects.get(id=data["supplier"])
            inputs = Inputs.objects.create(id=2, supplier=supp, discount=data["discount"], date=datetime.datetime.strptime(data["date"], "%Y-%m-%dT%H:%M"))
            inputs.save()

            products = data['products']
        
            for product in products:
                try:
                    p1 = Products.objects.get(id=product)
                    inputs.products.add(p1)
                    
                except Exception:
                    resp = {"exception": "Error in post! Could not find product!"}
                    status = 404
                    return Response(resp, status)
                
            status = 200
            resp = {"status": "New input successfully registered!"}

        except:
            resp = {"exception": "Error in post! Could not find supplier!"}
            status = 404

        return Response(resp, status)

    def put(self, request):
        data = request.data 

        try:
            inputs = Inputs.objects.get(id=data["id"])
            inputs.date = datetime.datetime.strptime(data["date"], "%Y-%m-%dT%H:%M")
            inputs.discount = data["discount"]

            supplier = Suppliers.objects.get(id=data["supplier"])
            inputs.supplier = supplier
            inputs.save()

            inputs.products.clear()
            products = data['products']
        
            for product in products:
                try:
                    p1 = Products.objects.get(id=product)
                    inputs.products.add(p1)
                    
                except Exception:
                    status = 404
                    resp = {"status": "Error in update! Could not find product!"}
                    return Response(resp, status)
                
            inputs.save()

            resp = {"status": "Update confirmed!"}
            status = 200

        except:
            resp = {"exception": "Could not find requested input!"}
            status = 404

        return Response(resp, status)

    def delete(self, request):
        data = request.data

        try:
            inputs = Inputs.objects.get(id=data["id"])
            inputs.delete()

            resp = {"status": "Input successfully deleted!"}
            status = 200
        
        except:
            resp = {"exception": "Could not find requested input!"}
            status = 404

        return Response(resp, status)
    

class Message(APIView):
    # REST API view to handle user messages
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser,)

    def get(self, request):
        data = request.query_params

        try:
            if "message_id" in list(data.keys()):
                messages = Messages.objects.get(pk=data["message_id"])
                serializer = MessageSerializer(messages)
                        
            if "sender" in list(data.keys()):
                sender = User.objects.get(pk=data["sender"])
                messages = Messages.objects.filter(sender=sender)
                serializer = MessageSerializer(messages, many=True)

            if len(data) == 0:
                messages = Messages.objects.all()
                serializer = MessageSerializer(messages, many=True)
        except:
            status = 404
            resp = {"status": "Error retriving messages!"}
            return Response(resp, status=status)

        resp = serializer.data

        return Response(resp)
        

    def post(self, request):
        data = request.data
        
        try:
            sender = User.objects.get(pk=data["sender"])
            receiver = User.objects.get(pk=data["receiver"])
        except:
            resp = {"status": "Couldn't find user for sender and/or receiver!"}
            status = 404
            return Response(resp, status=status)
        message = Messages(sender=sender, receiver=receiver, date=data["date"], message=data["message"])
        message.save()

        resp = {"status": "Message sent!"}

        return Response(resp)

    def delete(self, request):
        data = request.data

        try:
            message = Messages.objects.get(pk=data["message_id"])
            message.delete()

            resp = {"status": "Message deleted!"}
            status = 200
        except:
            resp = {"status": "Couldn't find requested message!"}
            status = 404

        return Response(resp, status=status)


# Web pages (front-end)

class ControlOrders(generic.ListView):
    # View that gives employees in the kitchen full control of the orders made by waiters
    template_name = 'orders/orders.html'
    context_object_name = 'all_orders'

    def get_queryset(self):
        context = read_config()
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
        context = read_config()
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
        context = read_config()
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
        
        if 'delete_btn' in request.POST.keys() and request.POST['delete_btn'] != '':
            try:
                product = Products.objects.get(pk=request.POST['delete_btn'])
                product.delete()
            except:
                return render(request=request, template_name="orders/error.html", context={"message": "Could not find id to delete!"}, status=404)
        
            return redirect('products')
    

class ListSuppliers(generic.ListView):
    # View that lists all suppliers, allowing deletion and inclusion of new ones.
    template_name = "orders/suppliers.html"
    context_object_name = "suppliers"

    def get_queryset(self) -> QuerySet[Any]:
        context = read_config()
        return Suppliers.objects.all().order_by('name')
    
    def post(self, request):
        if 'search' in request.POST.keys() and request.POST['search'] != '':
            supp_id = request.POST['search']
            if supp_id.isdecimal():
                supplier = Suppliers.objects.filter(pk=int(supp_id))
            else:
                supplier = Suppliers.objects.filter(name=supp_id)
            context = {'suppliers': supplier}

            return render(request, 'order/suppliers.html', context)
        
        if 'delete_btn' in request.POST.keys() and request.POST['delete_btn'] != '':
            try:
                suppli = Suppliers.objects.get(pk=request.POST['delete_btn'])
                suppli.delete()
            except:
                return render(request=request, template_name="orders/error.html", context={"message": "Could not find id to delete!"}, status=404)
        
            return redirect('suppliers')
    

class ListUsers(generic.ListView):
    # View that lists all users, allowing deletion and inclusion of new ones.
    template_name = "orders/users.html"
    context_object_name = "users"

    def get_queryset(self) -> QuerySet[Any]:
        context = read_config()
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


def read_config():
    arq = os.path.join(settings.BASE_DIR, 'orders/static/config.json')
    context = {}
    if not os.path.exists(arq):
        cmp = {"name":"Test Name", "address":"0000 Test Address", "phone":"00000000", "logo":"default_logo.jpg", "language": "en-us"}
        with open(arq, "w") as arq_json:
            arq_json.write(json.dumps(cmp))
        context["language"] = cmp["language"]
        context["logo"] = cmp["logo"]
    else:
        with open(arq, "r") as arq_json:
            config=json.load(arq_json)
            if len(config) == 0:
                config = {"name":"Test Name", "address":"0000 Test Address", "phone":"00000000", "logo":"default_logo.jpg", "language": "en-us"}
            context["language"] = config["language"]
            context["logo"] = config["logo"]

    translation.activate(context["language"])
    return context


def home(request):
    context = read_config()
    return render(request, "orders/index.html", context)


def new_order(request):
    # View for making new orders from the browser
    config = read_config()
    if request.method == "GET":
        products = Products.objects.all()
        context = {"products": products}
        context["language"] = config["language"]
        context["logo"] = config["logo"]
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
    context = read_config()
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
    context = read_config()
    if request.method == 'GET':
        return render(request, 'orders/newuser.html', context)
    
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']

        u = User.objects.create_user(username=username, email=email)
        u.save()

        return redirect('home')
    

def delete_user(request):
    context = read_config()
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
    context = read_config()
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
    context = read_config()
    arq = os.path.join(settings.BASE_DIR, 'orders/static/config.json') 
    
    if request.method == "GET":
        with open(arq, "r") as arq_json:
            if os.stat(arq).st_size != 0:
                config=json.load(arq_json)
                context["company"] = config
            else:
                context["company"] = cmp
        return render(request, 'orders/company_info.html', context)
    
    if request.method == "POST":
        cmp = {}
        logo_file = "logo" + str(datetime.date.today().year) + str(datetime.date.today().month) + str(datetime.date.today().day) + ".jpg"
        with open(arq, "w") as arq_json:
            cmp["name"] = request.POST["name"]
            cmp["address"] = request.POST["address"]
            cmp["phone"] = request.POST["phone"]
            cmp["logo"] = logo_file
            cmp["language"]= request.POST["language"]
            arq_json.write(json.dumps(cmp))

        img_file = os.path.join(settings.BASE_DIR, 'media/'+logo_file)

        with open(img_file, "wb") as logo:
            logo.write(request.FILES.get("logo").file.read())

        return redirect("info")
    

def system_conf(request):
    context = read_config()
    arq = os.path.join(settings.BASE_DIR, 'orders/static/config.json')

    if request.method == "GET":
        return render(request, 'orders/system-conf.html', context)
    
    if request.method == "POST":
        with open(arq, "r") as arq_json:
            config=json.load(arq_json)
        with open(arq, "w") as arq_json:
            config["language"] = request.POST["language"]
            context["language"] = config["language"]
            arq_json.write(json.dumps(config))

        translation.activate(context["language"])
        
        return render(request, 'orders/system-conf.html', context)