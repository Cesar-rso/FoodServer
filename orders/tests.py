from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework import status
from .models import *
from .views import *
import datetime


class ProductAPITest(APITestCase):
    def setUp(self):
        sup = Suppliers.objects.create(id=1, name='testSupplier', address='test address', phone='01532334567', supply_type='test')
        Products.objects.create(id=1, name='testProduct', description='-test-', price=2.56, cost=1.80, supplier=sup)
        Products.objects.create(id=2, name='testProduct 2', description='-test-', price=4.16, cost=2.12, supplier=sup)

    def test_url(self):  # Verifying if the correct url resolves
        url = reverse('api-product')
        self.assertEqual(resolve(url).func.view_class, Product)

    def test_CheckCorrectID(self):
        product = Products.objects.all().first()
        search = {"id": product.pk}
        url = reverse('api-product')

        response = self.client.get(url, search)
        product_data = {"id": 1, "name": "testProduct", "description": "-test-", "price": 2.56, "cost": 1.80,
                                         "picture": "/media/default.jpg", "supplier": 1}

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, product_data)

    def test_CheckWrongID(self):
        search = {"id": 5}
        url = reverse('api-product')

        response = self.client.get(url, search)
        product_data = {"exception": "Couldn't find requested product!"}

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, product_data)

    def test_POSTnewProduct(self):

        product_data = {"name": "testProduct 3", "description": "-test-", "price": 3.15, "cost": 0.60,
                                         "picture": "/media/default.jpg", "supplier": 1}
        url = reverse('api-product')
        response = self.client.post(url, product_data, format="json")
        all_products = Products.objects.all()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(all_products.count(), 3)

    def test_UpdateProduct(self):
        product_data = {"id": 1,"name": "testProduct 1", "description": "-test-", "price": 3.52, "cost": 1.60,
                                         "picture": "/media/default.jpg", "supplier": 1}
        url = reverse('api-product')
        response = self.client.put(url, product_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prod = Products.objects.get(id=1)
        self.assertEqual(prod.price, product_data["price"])
        self.assertEqual(prod.description, product_data["description"])

    def test_UpdateProductWrongID(self):
        product_data = {"id": 9,"name": "testProduct 1", "description": "-test-", "price": 8.52, "cost": 1.60,
                                         "picture": "/media/default.jpg", "supplier": 1}
        url = reverse('api-product')
        response = self.client.put(url, product_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_DeleteProductWrongID(self):
        product_data = {"id": 9}

        url = reverse('api-product')
        response = self.client.delete(url, product_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_DeleteProduct(self):
        product_data = {"id": 2}

        url = reverse('api-product')
        response = self.client.delete(url, product_data, format="json")
        all_products = Products.objects.all()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(all_products.count(), 1)


class OrderAPITest(APITestCase):

    def setUp(self):
        sup = Suppliers.objects.create(id=1, name='testSupplier', address='test address', phone='01532334567', supply_type='test')
        test_product = Products.objects.create(id=1, name='testProduct', description='-test-', price=2.56, cost=1.80, supplier=sup)
        test_product.save()
        test_product2 = Products.objects.create(id=2, name='testProduct2', description='-test2-', price=3.88, cost=2.80, supplier=sup)
        test_product2.save()
        test_order = Orders.objects.create(table=1, status='WA')
        test_order.save()
        test_order.product.add(test_product)

        self.user = User.objects.create(username='test')
        self.user.set_password('passtest')
        self.user.save()

        Payments.objects.create(value=0.0, user=self.user)
        Token.objects.create(user=self.user)

    def test_url(self):
        url = reverse('api-orders')
        self.assertEqual(resolve(url).func.view_class, Order)

    def test_CancelWithNoCredentials(self):
        data = {"table": 1}

        response = self.client.delete(reverse('api-orders'), data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_CancelWithCredentials(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        data = {"table": 1}

        response = self.client.delete(reverse('api-orders'), data=data, format="json")
        order = Orders.objects.filter(table=1).order_by('date')[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.status, Orders.Status.CANCELED)

    def test_CancelWithWrongData(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        data = {"table": 5}

        response = self.client.delete(reverse('api-orders'), data=data, format="json")
        order = Orders.objects.filter(table=1).order_by('date')[0]
        rt_data = {"exception": "Couldn't find requested order!"}

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(order.status, Orders.Status.WAITING)
        self.assertEqual(response.data, rt_data)

    def testCheckOrderWithExistingTable(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        data = {"table": 1}
        response = self.client.get(reverse("api-orders"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testCheckOrderWithWrongTableNumber(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        data = {"table": 5}
        resp = {"exception": "Couldn't find requested order!"}
        response = self.client.get(reverse("api-orders"), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, resp)

    def testPlaceOrderWithCorrectDataNoToken(self):
        data = {"products": {"product1": 1, "product2": 2}, "table": 1, "status": "WA"}
        response = self.client.post(reverse("api-orders"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def testPlaceOrderWithCorrectDataWithToken(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        data = {"products": {"product1": 1, "product2": 2}, "table": 1, "status": "WA"}
        response = self.client.post(reverse("api-orders"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "Order placed!")

        order = Orders.objects.get(id=2)
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
        response = self.client.post(reverse("api-orders"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["status"], "Error! Could not find product!")


class MessagesAPITest(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(username='test')
        self.user.set_password('passtest')
        self.user.save()

        self.user2 = User.objects.create(username='test2')
        self.user2.set_password('passtest2')
        self.user2.save()

        Messages.objects.create(sender=self.user, receiver=self.user2, date=datetime.datetime.now(), message="setUp message")
        Messages.objects.create(sender=self.user, receiver=self.user2, date=datetime.datetime.now(), message="setUp message 2")

        Token.objects.create(user=self.user)

    def test_url(self):
        url = reverse('api-message')
        self.assertEqual(resolve(url).func.view_class, Message)

    def test_postNewMessage(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        data = {'sender': self.user2.pk, 'receiver': self.user.pk, 'date': str(datetime.datetime.now()), "message": "test message 1"}
        response = self.client.post(reverse('api-message'), data=data, format="json")
        message = Messages.objects.all().order_by("date").last()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(message.message, "test message 1")

    def test_getAllMessages(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        response = self.client.get(reverse('api-message'))
        messages = Messages.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(messages.count(), 2)

    def test_getMessagesFromUser(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        data = {"sender": 1}
        response = self.client.get(reverse('api-message'), data)
        messages = Messages.objects.filter(sender=self.user)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(messages.count(), 2)
        for msg in response.json():
            self.assertEqual(msg["sender"], self.user.pk)
            self.assertEqual(msg["receiver"], self.user2.pk)

    def test_getSpecificMessage(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        data = {"message_id": 2}
        response = self.client.get(reverse('api-message'), data)
        resp_data = response.json()
        if len(resp_data.keys()) > 1:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["sender"], 1)
            self.assertEqual(response.json()["receiver"], 2)
            self.assertEqual(response.json()["message"], "setUp message 2")
        else:
            self.fail("API not returning expected data!")

    def test_getSpecificMessageWrongId(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        data = {"message_id": 4}
        response = self.client.get(reverse('api-message'), data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_getMessagesFromInexistentUser(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        data = {"sender": 4}
        response = self.client.get(reverse('api-message'), data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_postNewMessageWithInexistentSender(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        data = {'sender': 9, 'receiver': 2, 'date': "2024-04-22", "message": "test message 1"}
        response = self.client.post(reverse('api-message'), data=data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_postNewMessageWithInexistentReceiver(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        data = {'sender': 1, 'receiver': 9, 'date': "2024-04-22", "message": "test message 1"}
        response = self.client.post(reverse('api-message'), data=data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_DeleteMessageWrongId(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        data = {"message_id": 7}
        response = self.client.delete(reverse('api-message'), data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_DeleteMessage(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        messages_count = Messages.objects.all().count()

        data = {"message_id": 1}
        response = self.client.delete(reverse('api-message'), data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        messages = Messages.objects.all()
        self.assertLess(messages.count(), messages_count)


class SuppliersAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')
        self.user.set_password('passtest')
        self.user.save()

        Suppliers.objects.create(name="test supplier", address="test address", phone=11223456, supply_type="test data")

        Token.objects.create(user=self.user)

    def test_url(self):
        url = reverse('api-supplier')
        self.assertEqual(resolve(url).func.view_class, Supplier)

    def test_POSTnewSupplier(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        url = reverse('api-supplier')
        data = {"name": "test supplier 2", "address": "test address 2", "phone": 12345678, "supply_type": "test data"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sups = Suppliers.objects.all().count()
        self.assertEqual(sups, 2)
        sups = Suppliers.objects.get(id=2)
        self.assertEqual(sups.name, "test supplier 2")

    def test_POSTnewSupplierNoCredentials(self):
        url = reverse('api-supplier')
        data = {"name": "test supplier 2", "address": "test address 2", "phone": 12345678, "supply_type": "test data"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_GetAllSuppliersWithCredentials(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        url = reverse('api-supplier')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sups = Suppliers.objects.all().count()
        self.assertEqual(sups, 1)

    def test_GetAllSuppliersNoCredentials(self):
        url = reverse('api-supplier')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_GetSpecificSupplierWithCredentials(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        url = reverse('api-supplier')
        data = {"id": 1}
        response = self.client.get(url, data, format="json")

        supp = Suppliers.objects.get(id=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(supp.name, response.data["name"])

    def test_GetSpecificSupplierWrongID(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        url = reverse('api-supplier')
        data = {"id": 9}
        response = self.client.get(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_UpdateSupplierNoCredentials(self):
        url = reverse('api-supplier')
        data = {"id": 1, "name": "test supplier 1", "address": "test address 1", "phone": 11223456, "supply_type": "test data"}
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_UpdateSupplierWrongID(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        url = reverse('api-supplier')
        data = {"id": 9, "name": "test supplier 1", "address": "test address 1", "phone": 11223456, "supply_type": "test data"}
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_UpdateSupplierWithCredentials(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')
        
        url = reverse('api-supplier')
        data = {"id": 1, "name": "test supplier 1", "address": "test address 1", "phone": 11223456, "supply_type": "test data"}
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_DeleteNoCredentials(self):
        url = reverse('api-supplier')
        data = {"id": 1}

        response = self.client.delete(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_DeleteWithCredentialsWrongID(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        url = reverse('api-supplier')
        data = {"id": 9}

        response = self.client.delete(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_DeleteWithCredentials(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        url = reverse('api-supplier')
        data = {"id": 1}

        response = self.client.delete(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        supps = Suppliers.objects.all().count()
        self.assertEqual(supps, 0)


class InputsAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')
        self.user.set_password('passtest')
        self.user.save()
        self.date = datetime.datetime.now()

        supp = Suppliers.objects.create(name="test supplier", address="test address", phone=11223456, supply_type="test data")
        prod = Products.objects.create(id=1, name='testProduct', description='-test-', price=2.56, cost=1.80, supplier=supp)
        inp = Inputs.objects.create(supplier=supp, date=self.date, discount=10)
        inp.products.add(prod)
        inp.save()

        Token.objects.create(user=self.user)

    def test_url(self):
        url = reverse('api-input')
        self.assertEqual(resolve(url).func.view_class, Input)

    def test_PostNewInputNoCredentials(self):
        url = reverse('api-input')
        data = {"supplier": 1, "discount": 5, "date": str(datetime.datetime.now()), "products": [1]}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_PostNewInputWrongSupplier(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        url = reverse('api-input')
        data = {"supplier": 7, "discount": 5, "date": str(datetime.datetime.now()), "products": [1]}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_PostNewInputWrongProduct(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        url = reverse('api-input')
        data = {"supplier": 1, "discount": 5, "date": str(datetime.datetime.now()), "products": [7]}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_PostNewInput(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        url = reverse('api-input')
        data = {"supplier": 1, "discount": 5, "date": str(datetime.datetime.now()), "products": [1]}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_GetInputNoCredentials(self):
        url = reverse('api-input')
        data = {"id": 1}

        response = self.client.get(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_GetInputWithCredentialsWrongID(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        url = reverse('api-input')
        data = {"id": 11}

        response = self.client.get(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_GetInputWithCredentialsWrongSupplier(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        url = reverse('api-input')
        data = {"supplier": 7}

        response = self.client.get(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_GetAllInputs(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        url = reverse('api-input')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_GetSpecificInputWithCredentials(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        url = reverse('api-input')
        data = {"id": 1}

        response = self.client.get(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 1)
        self.assertEqual(response.data["discount"], 10)
        self.assertEqual(response.data["supplier"], 1)
        self.assertEqual(response.data["date"], str(self.date))

    def test_GetInputsWithSpecificSupplierWithCredentials(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        url = reverse('api-input')
        data = {"supplier": 1}

        response = self.client.get(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data["id"], 1)
        self.assertEqual(response.data["discount"], 10)
        self.assertEqual(response.data["supplier"], 1)
        self.assertEqual(response.data["date"], str(self.date))

    def test_GetInputsWithSpecificDateWithCredentials(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        url = reverse('api-input')
        data = {"date": str(self.date)}

        response = self.client.get(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data["id"], 1)
        self.assertEqual(response.data["discount"], 10)
        self.assertEqual(response.data["supplier"], 1)
        self.assertEqual(response.data["date"], str(self.date))

    def test_DeleteInputNoCredentials(self):
        url = reverse('api-input')
        data = {"id": 1}

        response = self.client.delete(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_DeleteInputWithCredentialsWrongID(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        url = reverse('api-input')
        data = {"id": 9}

        response = self.client.delete(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_DeleteInputWithCredentials(self):
        check_login = self.client.login(username='test', password='passtest')
        self.assertTrue(check_login)

        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0].key}')

        url = reverse('api-input')
        data = {"id": 1}

        response = self.client.delete(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        inps = Inputs.objects.all()
        self.assertEqual(len(inps), 0)


class OrdersTestCase(TestCase):

    def setUp(self):
        user = User.objects.create(username='test')
        user.set_password('passtest')
        user.save()
        Payments.objects.create(value=0.0, user=user)
        sup = Suppliers.objects.create(id=1, name='testSupplier', address='test address', phone='01532334567', supply_type='test')
        test_product = Products.objects.create(name='testProduct', description='-test-', price=2.56, cost=1.80, supplier=sup)
        test_product.save()
        test_order = Orders.objects.create(table=1, status='WA')
        test_order.save()
        test_order.product.add(test_product)

    def test_url(self):  # Verifying if the correct url resolves
        url = reverse('orders')
        self.assertEqual(resolve(url).func.view_class, ControlOrders)

    def test_OrdersGET(self):
        response = self.client.get(reverse('orders'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'orders/orders.html')

    def test_OrdersPOST(self):
        response = self.client.post(reverse('orders'), {'submit': 1, 'status': 'PP'})
        current_status = Orders.objects.get(pk=1).status
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(current_status, 'PP')

    def test_OrdersDELETE(self):
        order_to_delete = Orders.objects.all().first().pk
        response = self.client.post(reverse('orders'), {'delete': order_to_delete, 'status': 'PP'})
        orders = Orders.objects.all()
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(orders.count(), 1)


class CheckoutTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username='test')
        user.set_password('passtest')
        user.save()
        Payments.objects.create(value=0.0, user=user)
        sup = Suppliers.objects.create(id=1, name='testSupplier', address='test address', phone='01532334567', supply_type='test')
        test_product = Products.objects.create(name='testProduct', description='-test-', price=2.56, cost=1.80, supplier=sup)
        test_product.save()
        test_order = Orders.objects.create(table=1, status='WA')
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
        orders = Orders.objects.all()
        self.assertNotEqual(orders.count(), 0)

    def test_payOrders(self):
        self.client.login(username='test', password='passtest')
        response = self.client.post(reverse('pay_orders'), {'pay': 1})
        self.status = Orders.objects.all().first().status
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(self.status, 'PA')


class ProductsTestCase(TestCase):
    def setUp(self):
        sup = Suppliers.objects.create(id=1, name='testSupplier', address='test address', phone='01532334567', supply_type='test')
        test_product = Products.objects.create(id=1, name='testProduct', description='-test-', price=2.56, cost=1.80, supplier=sup)
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
        data = {"delete_btn": 1}
        response = self.client.post(reverse('products'), data=data, format='json')
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
