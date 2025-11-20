from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('submit/<str:product_slug>/', views.submit_review, name='submit_review'),
    path('submit-ajax/<int:product_id>/', views.submit_review_ajax, name='submit_review_ajax'),
    path('get/<str:product_slug>/', views.get_product_reviews, name='get_reviews'),
    path('delete/<int:review_id>/', views.delete_review, name='delete_review'),
]

