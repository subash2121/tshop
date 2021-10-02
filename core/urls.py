from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import decorators, views as auth_views
from core import views
from .views import (
    remove_from_cart,
    reduce_quantity_item,
    add_to_cart,
    ProductView,
    HomeView,
    OrderSummaryView,
    CheckoutView,
    OrderSummaryVieww,
    delete_product,
    t_profile,
    t_order_val,
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product/<pk>/', ProductView.as_view(), name='product'),
    path('add-to-cart/<pk>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<pk>/', remove_from_cart, name='remove-from-cart'),
    path('order-summary', OrderSummaryView.as_view(), 
        name='order-summary'),
   path('reduce-quantity-item/<pk>/', reduce_quantity_item,
        name='reduce-quantity-item'),
    path('delete-product/<pk>/', delete_product,
        name='delete-product'),
    path('my-orders',views.OrderSummaryVieww,name='OrderSummaryVieww'),
    path('tribal-home/',views.t_home,name='t_home'),
    path('tribal-profile/',views.t_profile,name='t_profile'),
    path('tribal-orders/<pk>/',views.t_order_val,name='t_order_val'),
    path('tribal-orders/',views.t_orders,name='t_orders'),
    path('my-products/',views.products,name='products'),
    path('sign-in/',auth_views.LoginView.as_view(template_name="sign_in.html")),
    path('sign-out/',auth_views.LogoutView.as_view(next_page="/")),
    path('sign-up/',views.sign_up),
    path('profile/',views.profile_page,name='profile'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),

]
if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)