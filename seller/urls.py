from django.urls import path
from . import views

app_name = 'seller'

urlpatterns = [
    path('dashboard/', views.seller_dashboard, name='dashboard'),
    path('order/<str:order_number>/', views.seller_order_detail, name='order_detail'),
    path('update-status/<str:order_number>/', views.update_order_status, name='update_order_status'),
]

