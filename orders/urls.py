from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [path('', views.home, name='home'),
               path('api/order', views.Order.as_view(), name='api-orders'),
               path('checkout', views.Checkout.as_view(), name='checkout'),
               path('api/product', views.Product.as_view(), name='check-product'),
               path('api/supplier', views.Supplier.as_view(), name='api-supplier'),
               path('orders', views.ControlOrders.as_view(), name='orders'),
               path('api/auth_token', obtain_auth_token, name='api_token'),
               path('reports', views.reports, name='reports'),
               path('initial_password', views.initial_password, name="initial_password"),
               path('new_user', views.new_user, name="new_user"),
               path('delete_user', views.delete_user, name="delete_user"),
               path('login', views.login_request, name='login'),
               path('logout', views.logout_request, name='logout'),
               path('new_order', views.new_order, name='new_order'),
               path('pay_orders', views.pay_orders, name='pay_orders'),
               path('products', views.ListProducts.as_view(), name='products'),
               path('suppliers', views.ListSuppliers.as_view(), name='suppliers'),
               path('new_product', views.ProductRegistration.as_view(), name='reg_product'),
               path('new_supplier', views.SupplierRegistration.as_view(), name='reg_supplier'),
               path('update_supplier/<pk>', views.SupplierUpdate.as_view(), name="update_supplier"),
               path('update_product/<pk>', views.ProductUpdate.as_view(), name="update_product"),
               path('update_user/<pk>', views.UserUpdate.as_view(), name="update_user")] \
              + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


