"""
URL configuration for aromas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView

from django.conf import settings
from django.conf.urls.static import static

from . import views
from .admin_utils import download_database
from accounts.views import honeypot_admin_login

urlpatterns = [
    path('admin/', honeypot_admin_login, name='admin_honeypot'),
    path(f'{settings.ADMIN_URL}download-database/', download_database, name='admin_download_database'),
    path(settings.ADMIN_URL, admin.site.urls),
    path('', views.home, name='home'),
    path('store/', include('store.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include(('orders.urls', 'orders'), namespace='orders')),
    path('seller/', include(('seller.urls', 'seller'), namespace='seller')),
    path('wishlist/', include(('wishlist.urls', 'wishlist'), namespace='wishlist')),
    path('reviews/', include(('reviews.urls', 'reviews'), namespace='reviews')),
    path('coupons/', include(('coupons.urls', 'coupons'), namespace='coupons')),
    path('loyalty/', include(('loyalty.urls', 'loyalty'), namespace='loyalty')),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('returns-refunds/', views.returns_policy, name='returns_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('shipping-policy/', views.shipping_policy, name='shipping_policy'),
    path('disclaimer/', views.disclaimer_policy, name='disclaimer_policy'),
    path('cancellation-policy/', views.cancellation_policy, name='cancellation_policy'),
    path('contact-us/', views.contact_us, name='contact_us'),
    # Redirect old cart.html to new cart URL
    path('cart.html', RedirectView.as_view(url='/cart/', permanent=True)),
    
    # Secure media serving - serves media files through Django to hide file paths
    re_path(r'^media/(?P<path>.*)$', views.secure_media, name='secure_media'),
]

# Only serve media files directly in development (DEBUG mode)
# In production, media files are served through the secure_media view above
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
