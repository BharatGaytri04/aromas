from django.shortcuts import render
from django.utils import timezone

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