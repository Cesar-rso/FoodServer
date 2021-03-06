from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Order, Products, Payments
from .views import ControlOrders, login_request, Checkout, ListProducts, CheckProduct, CancelOrder, CheckOrder, \
    PlaceOrder


class CheckProductAPITest(APITestCase):
    def setUp(self):
        Products.objects.create(id=1, name='testProduct', description='-test-', price=2.56)

    def test_url(self):  # Verifying if the correct url resolves
        url = reverse('check-product')
        self.assertEqual(resolve(url).func.view_class, CheckProduct)

    def test_correctID(self):
        product = Products.objects.all().first()
        search = {"id": product.pk}
        url = reverse('check-product')

        response = self.client.get(url, search)
        product_data = {"id": 1, "name": "testProduct", "description": "-test-", "price": 2.56,
                                         "picture": "/media/default.jpg"}

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, product_data)

    def test_wrongID(self):
        search = {"id": 2}
        url = reverse('check-product')

        response = self.client.get(url, search)
        product_data = {"exception": "Couldn't find requested product!"}

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, product_data)


class CancelOrderAPITest(APITestCase):

    def setUp(self):
        test_product = Products.objects.create(id=1, name='testProduct', description='-test-', price=2.56)
        test_product.save()
        test_order = Order.objects.create(table=1, status='WA')
        test_order.save()
        test_order.product.add(test_product)

        self.user = User.objects.create(username='test')
        self.user.set_password('passtest')
        self.user.save()

        Payments.objects.create(value=0.0, user=self.user)
        Token.objects.create(user=self.user)

    def test_url(self):
        url = reverse('cancel-order')
        self.assertEqual(resolve(url).func.view_class, CancelOrder)

    def test_CancelWithNoCredentials(self):
        data = {"table": 1}

        response = self.client.post(reverse('cancel-order'), data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_CancelWithCredentials(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        data = {"table": 1}

        response = self.client.post(reverse('cancel-order'), data=data, format="json")
        order = Order.objects.filter(table=1).order_by('date')[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.status, Order.Status.CANCELED)

    def test_CancelWithWrongData(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        data = {"table": 5}

        response = self.client.post(reverse('cancel-order'), data=data, format="json")
        order = Order.objects.filter(table=1).order_by('date')[0]
        rt_data = {"exception": "Couldn't find requested product!"}

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.status, Order.Status.WAITING)
        self.assertEqual(response.data, rt_data)


class CheckOrderAPITest(APITestCase):

    def setUp(self):
        user = User.objects.create(username='test')
        user.set_password('passtest')
        user.save()
        Payments.objects.create(value=0.0, user=user)
        test_product = Products.objects.create(id=1, name='testProduct', description='-test-', price=2.56)
        test_product.save()
        test_order = Order.objects.create(table=1, status='WA')
        test_order.save()
        test_order.product.add(test_product)

    def test_url(self):  # Verifying if the correct url resolves
        url = reverse('check-order')
        self.assertEqual(resolve(url).func.view_class, CheckOrder)

    def testCheckOrderWithExistingTable(self):
        data = {"table": 1}
        response = self.client.get(reverse("check-order"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # print(response.data)

    def testCheckOrderWithWrongTableNumber(self):
        data = {"table": 5}
        resp = {"exception": "Couldn't find requested order!"}
        response = self.client.get(reverse("check-order"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, resp)


class PlaceOrdersAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')
        self.user.set_password('passtest')
        self.user.save()
        Payments.objects.create(value=0.0, user=self.user)
        test_product = Products.objects.create(id=1, name='testProduct', description='-test-', price=2.56)
        test_product.save()
        test_product2 = Products.objects.create(id=2, name='testProduct2', description='-test2-', price=3.88)
        test_product2.save()

    def test_url(self):  # Verifying if the correct url resolves
        url = reverse('place-order')
        self.assertEqual(resolve(url).func.view_class, PlaceOrder)

    def testPlaceOrderWithCorrectDataNoToken(self):
        data = {"products": {"product1": 1, "product2": 2}, "table": 1, "status": "WA"}
        response = self.client.post(reverse("place-order"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def testPlaceOrderWithCorrectDataWithToken(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        data = {"products": {"product1": 1, "product2": 2}, "table": 1, "status": "WA"}
        response = self.client.post(reverse("place-order"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "Order placed!")

        order = Order.objects.all().first()
        self.assertEqual(order.status, "WA")
        self.assertEqual(order.table, 1)
        pk_counter = 1
        for product in order.product.all():
            self.assertEqual(product.pk, pk_counter)
            pk_counter += 1
            if product.pk == 1:
                self.assertEqual(product.name, "testProduct")
                self.assertEqual(product.description, "-test-")
                self.assertEqual(product.price, 2.56)
            if product.pk == 2:
                self.assertEqual(product.name, "testProduct2")
                self.assertEqual(product.description, "-test2-")
                self.assertEqual(product.price, 3.88)

    def testPlaceOrderWithWrongDataWithToken(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        data = {"products": {"product1": 3}, "table": 1, "status": "WA"}
        response = self.client.post(reverse("place-order"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "Error! Could not find product!")


class OrdersTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username='test')
        user.set_password('passtest')
        user.save()
        Payments.objects.create(value=0.0, user=user)
        test_product = Products.objects.create(name='testProduct', description='-test-', price=2.56)
        test_product.save()
        test_order = Order.objects.create(table=1, status='WA')
        test_order.save()
        test_order.product.add(test_product)

    def test_url(self):  # Verifying if the correct url resolves
        url = reverse('orders')
        self.assertEqual(resolve(url).func.view_class, ControlOrders)

    def test_OrdersGET(self):
        response = self.client.get(reverse('orders'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'orders/index.html')

    def test_OrdersPOST(self):
        response = self.client.post(reverse('orders'), {'submit': 1, 'status': 'PP'})
        current_status = Order.objects.get(pk=1).status
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(current_status, 'PP')

    def test_OrdersDELETE(self):
        order_to_delete = Order.objects.all().first().pk
        response = self.client.post(reverse('orders'), {'delete': order_to_delete, 'status': 'PP'})
        orders = Order.objects.all()
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(orders.count(), 0)


class CheckoutTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username='test')
        user.set_password('passtest')
        user.save()
        Payments.objects.create(value=0.0, user=user)
        test_product = Products.objects.create(name='testProduct', description='-test-', price=2.56)
        test_product.save()
        test_order = Order.objects.create(table=1, status='WA')
        test_order.save()
        test_order.product.add(test_product)

    def test_url(self):  # Verifying if the correct url resolves
        url = reverse('checkout')
        self.assertEqual(resolve(url).func.view_class, Checkout)

    def test_CheckoutGET(self):
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'orders/checkout.html')

    def test_CheckoutPOST(self):
        response = self.client.post(reverse('checkout'), {'search': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_CheckoutPOST_empty(self):
        response = self.client.post(reverse('checkout'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_CheckoutPOST_SQL_injection(self):
        response = self.client.post(reverse('checkout'), {'search': '\'); DELETE * FROM Order;'})
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        orders = Order.objects.all()
        self.assertNotEqual(orders.count(), 0)

    def test_payOrders(self):
        self.client.login(username='test', password='passtest')
        response = self.client.post(reverse('pay_orders'), {'pay': 1})
        self.status = Order.objects.all().first().status
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(self.status, 'PA')


class ProductsTestCase(TestCase):
    def setUp(self):
        test_product = Products.objects.create(name='testProduct', description='-test-', price=2.56)
        test_product.save()

    def test_url(self):
        url = reverse('products')
        self.assertEqual(resolve(url).func.view_class, ListProducts)

    def test_ProductsPOST_search(self):
        response = self.client.post(reverse('products'), {'search': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'orders/products.html')

    def test_ProductsPOST_search_SQL_Injection(self):
        response = self.client.post(reverse('products'), {'search': '1\'); DELETE * FROM Products;'})
        products = Products.objects.all().count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(products, 0)

    def test_ProductsPOST_delete(self):
        response = self.client.post(reverse('products'), {'submit': 1})
        products = Products.objects.all().count()
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(products, 0)


class LoginTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')
        self.user.set_password('passtest')
        self.user.save()

    def test_url(self):  # Verifying if the correct url resolves
        url = reverse('login')
        self.assertEqual(resolve(url).func, login_request)

    def test_correctLogin_API(self):
        response = self.client.login(username='test', password='passtest')
        self.assertTrue(response)

    def test_correctLogin_page(self):
        response = self.client.post(reverse('login'), {'username': 'test', 'password': 'passtest'})
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_wrongLogin_API(self):
        response = self.client.login(username='None', password='none')
        self.assertFalse(response)

    def test_wrongLogin_page(self):
        response = self.client.post(reverse('login'), {'username': 'Wrong', 'password': 'wrong'})
        self.assertTemplateUsed(response, 'orders/error.html')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
