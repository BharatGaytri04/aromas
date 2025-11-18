from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from category.models import Category
from .models import Product, Variation
from cart.models import Cart, CartItem


def store(request, category_slug=None):
    category = None
    products = None

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True).order_by('id')
    else:
        products = Product.objects.filter(is_available=True).order_by('id')

    # Pagination - 6 products per page
    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    # Check which products are in cart
    products_in_cart = []
    try:
        cart = Cart.objects.get(cart_id=_get_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        products_in_cart = [item.product.id for item in cart_items]
    except Cart.DoesNotExist:
        products_in_cart = []

    context = {
        'products': paged_products,
        'product_count': product_count,
        'selected_category': category,
        'products_in_cart': products_in_cart,
        'keyword': None,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, is_available=True)
    
    # Check if product is in cart
    in_cart = False
    try:
        cart = Cart.objects.get(cart_id=_get_cart_id(request))
        cart_item = CartItem.objects.filter(cart=cart, product=product).exists()
        in_cart = cart_item
    except Cart.DoesNotExist:
        in_cart = False
    
    colors = Variation.objects.filter(product=product, variation_category='color', is_active=True)
    sizes = Variation.objects.filter(product=product, variation_category='size', is_active=True)
    has_variations = colors.exists() or sizes.exists()
    
    context = {
        'product': product,
        'in_cart': in_cart,
        'colors': colors,
        'sizes': sizes,
        'has_variations': has_variations,
    }
    return render(request, 'product_detail.html', context)


def search(request):
    keyword = request.GET.get('keyword', '').strip()
    product_count = 0
    
    if keyword:
        # Search in product name and description using Q objects
        products = Product.objects.filter(
            Q(product_name__icontains=keyword) | Q(description__icontains=keyword),
            is_available=True
        ).distinct().order_by('id')
        product_count = products.count()
        
        # Pagination - 6 products per page
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
    else:
        products = Product.objects.none()
        paginator = Paginator(products, 6)
        paged_products = paginator.get_page(1)
        product_count = 0
    
    # Check which products are in cart
    products_in_cart = []
    try:
        cart = Cart.objects.get(cart_id=_get_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        products_in_cart = [item.product.id for item in cart_items]
    except Cart.DoesNotExist:
        products_in_cart = []
    
    context = {
        'products': paged_products,
        'product_count': product_count,
        'keyword': keyword,
        'selected_category': None,
        'products_in_cart': products_in_cart,
    }
    return render(request, 'store/store.html', context)


def _get_cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart