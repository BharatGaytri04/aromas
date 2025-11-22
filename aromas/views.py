from django.shortcuts import render
from django.utils import timezone
from django.http import FileResponse, Http404
from django.conf import settings
import os

from store.models import Product


def home(request):
    products = Product.objects.all().filter(is_available=True)
    print(products)  # debugging purpose for products
    print("products fetched successfully")  # debugging purpose for products
    context = {
        'products': products,
    }
    return render(request, 'home.html', context)


def _policy_context():
    return {
        'last_updated': timezone.now().strftime('%B %d, %Y'),
    }


def privacy_policy(request):
    return render(request, 'policies/privacy_policy.html', _policy_context())


def returns_policy(request):
    return render(request, 'policies/returns_policy.html', _policy_context())


def terms_conditions(request):
    return render(request, 'policies/terms_conditions.html', _policy_context())


def shipping_policy(request):
    return render(request, 'policies/shipping_policy.html', _policy_context())


def disclaimer_policy(request):
    return render(request, 'policies/disclaimer_policy.html', _policy_context())


def cancellation_policy(request):
    return render(request, 'policies/cancellation_policy.html', _policy_context())


def secure_media(request, path):
    """
    Serve media files securely through Django.
    This prevents direct access and hides full file paths.
    """
    # Optional: Add authentication check if needed
    # Uncomment the next 2 lines to require login for media access
    # if not request.user.is_authenticated:
    #     raise Http404("File not found")
    
    # Construct full file path
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    
    # Security: Prevent directory traversal attacks
    # Ensure the file is within MEDIA_ROOT
    file_path = os.path.normpath(file_path)
    media_root = os.path.normpath(str(settings.MEDIA_ROOT))
    
    if not file_path.startswith(media_root):
        raise Http404("File not found")
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise Http404("File not found")
    
    # Serve the file
    try:
        return FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')
    except IOError:
        raise Http404("File not found")