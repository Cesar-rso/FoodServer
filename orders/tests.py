from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from .models import Order, Products, Payments
from .views import ControlOrders, login_request


class OrdersTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username='test')
        user.set_password('passtest')
        user.save()
        Payments.objects.create(value=0.0, user=user)
        test_product = Products.objects.create(name='testProduct', description='-test-', price='2.56')
        test_product.save()
        test_order = Order.objects.create(table=1, status='WA')
        test_order.save()
        test_order.product.add(test_product)

    def test_url(self):  # Verifying if the correct url resolves
        url = reverse('orders')
        self.assertEqual(resolve(url).func.view_class, ControlOrders)

    def test_OrdersGET(self):
        response = self.client.get(reverse('orders'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/index.html')

    def test_OrdersPOST(self):
        response = self.client.post(reverse('orders'), {'submit': 1, 'status': 'PP'})
        current_status = Order.objects.get(pk=1).status
        self.assertEqual(response.status_code, 302)
        self.assertEqual(current_status, 'PP')

    def test_OrdersDELETE(self):
        order_to_delete = Order.objects.all().first().pk
        response = self.client.post(reverse('orders'), {'delete': order_to_delete, 'status': 'PP'})
        orders = Order.objects.all()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(orders.count(), 0)


class LoginTestCase(TestCase):

    def setUp(self):
        user = User.objects.create(username='test')
        user.set_password('passtest')
        user.save()

    def test_url(self):  # Verifying if the correct url resolves
        url = reverse('login')
        self.assertEqual(resolve(url).func, login_request)

    def test_correctLogin(self):
        response = self.client.login(username='test', password='passtest')
        self.assertTrue(response)

    def test_wrongLogin(self):
        response = self.client.login(username='None', password='none')
        self.assertFalse(response)
