from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('order-success/<str:order_number>/', views.order_success, name='order_success'),
    path('', views.order_list, name='order_list'),
    path('detail/<str:order_number>/', views.order_detail, name='order_detail'),
    path('invoice/<str:order_number>/', views.download_invoice, name='download_invoice'),
    path('return/<str:order_number>/', views.request_return, name='request_return'),
    # Razorpay payment URLs (will be active when Razorpay is enabled)
    path('razorpay/create/<str:order_number>/', views.create_razorpay_payment, name='create_razorpay_payment'),
    path('razorpay/callback/', views.razorpay_payment_callback, name='razorpay_payment_callback'),
]

