from django.shortcuts import render, get_object_or_404

from category.models import Category
from .models import Product


def store(request, category_slug=None):
    category = None
    products = None

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
        product_count = products.count()
    else:
        products = Product.objects.filter(is_available=True)
        product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
        'selected_category': category,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, is_available=True)
    return render(request, 'product_detail.html', {'product': product})