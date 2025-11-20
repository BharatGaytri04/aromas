from django.urls import path
from . import views

app_name = 'loyalty'

urlpatterns = [
    path('', views.loyalty_dashboard, name='dashboard'),
    path('generate-code/', views.generate_referral_code, name='generate_code'),
]

