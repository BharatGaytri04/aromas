from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Min, Max
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation

from category.models import Category
from .models import Product, Variation, Pincode
from cart.models import Cart, CartItem
from .utils import get_similar_products, get_frequently_bought_together, check_pincode_serviceability


def _get_cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def check_pincode(request):
    """Check pincode serviceability via AJAX"""
    if request.method == 'POST':
        pincode = request.POST.get('pincode', '').strip()
        
        if not pincode:
            return JsonResponse({'success': False, 'message': 'Please enter a pincode'})
        
        # Check in database first
        try:
            pincode_obj = Pincode.objects.get(pincode=pincode)
            return JsonResponse({
                'success': True,
                'serviceable': pincode_obj.is_serviceable,
                'city': pincode_obj.city,
                'state': pincode_obj.state,
                'delivery_days': pincode_obj.delivery_days,
                'cod_available': pincode_obj.cod_available,
                'message': f'Delivery available to {pincode_obj.city}, {pincode_obj.state}'
            })
        except Pincode.DoesNotExist:
            # Use utility function as fallback
            is_serviceable, message = check_pincode_serviceability(pincode)
            return JsonResponse({
                'success': True,
                'serviceable': is_serviceable,
                'message': message
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def _get_price_bounds():
    bounds = Product.objects.filter(is_available=True).aggregate(
        min_price=Min('price'),
        max_price=Max('price'),
    )
    min_price = bounds['min_price'] or 0
    max_price = bounds['max_price'] or min_price
    slider_min = 0
    slider_max = max(max_price, min_price + 1000, 5000)

    return {
        'min': min_price,
        'max': max_price,
        'slider_min': slider_min,
        'slider_max': slider_max,
    }


def _apply_product_filters(request, queryset):
    price_bounds = _get_price_bounds()

    filters = {
        'min_price': request.GET.get('min_price', ''),
        'max_price': request.GET.get('max_price', ''),
        'sale_only': request.GET.get('sale_only') == 'on',
        'in_stock': request.GET.get('in_stock') == 'on',
        'sort': request.GET.get('sort', 'newest'),
    }

    def parse_price(value):
        if value in (None, ''):
            return None
        try:
            price = Decimal(value)
            if price >= 0:
                return price
        except (InvalidOperation, TypeError):
            return None
        return None

    min_price_value = parse_price(filters['min_price'])
    max_price_value = parse_price(filters['max_price'])

    if min_price_value is not None:
        queryset = queryset.filter(price__gte=min_price_value)
    if max_price_value is not None:
        queryset = queryset.filter(price__lte=max_price_value)

    if filters['sale_only']:
        queryset = queryset.filter(sale_price__isnull=False)

    if filters['in_stock']:
        queryset = queryset.filter(stock__gt=0)

    sort_map = {
        'newest': '-created_date',
        'oldest': 'created_date',
        'price_low_high': 'price',
        'price_high_low': '-price',
        'name_asc': 'product_name',
        'name_desc': '-product_name',
    }
    queryset = queryset.order_by(sort_map.get(filters['sort'], '-created_date'))

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    clean_params = query_params.copy()
    for key in ['min_price', 'max_price']:
        if not query_params.get(key):
            clean_params.pop(key, None)
    current_query_string = clean_params.urlencode()
    filters_applied = any([
        min_price_value is not None,
        max_price_value is not None,
        filters['sale_only'],
        filters['in_stock'],
        filters['sort'] != 'newest'
    ])

    return queryset, filters, current_query_string, filters_applied, price_bounds


def store(request, category_slug=None):
    category = None

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
    else:
        products = Product.objects.filter(is_available=True)

    products, filters, current_query_string, filters_applied, price_bounds = _apply_product_filters(request, products)

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
        'keyword': request.GET.get('keyword'),
        'current_filters': filters,
        'filters_applied': filters_applied,
        'current_query_string': current_query_string,
        'price_bounds': price_bounds,
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
    
    # Get product images
    product_images = product.product_images.all()
    
    # Get reviews
    from reviews.models import Review
    reviews = Review.objects.filter(product=product, is_approved=True).order_by('-created_at')[:10]
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] if reviews.exists() else 0
    review_count = reviews.count()
    
    # Get user's review if exists
    user_review = None
    user_can_review = False
    user_has_reviewed = False
    
    if request.user.is_authenticated:
        # Check if user can review (has purchased the product)
        from orders.models import OrderProduct
        user_can_review = OrderProduct.objects.filter(
            user=request.user,
            product=product,
            ordered=True
        ).exists()
        
        # Check if user has already reviewed
        try:
            user_review = Review.objects.get(product=product, user=request.user)
            user_has_reviewed = True
        except Review.DoesNotExist:
            user_review = None
            user_has_reviewed = False
    
    # Get similar products
    similar_products = get_similar_products(product, limit=4)
    
    # Get frequently bought together
    frequently_bought = get_frequently_bought_together(product, limit=4)
    
    # Check if in wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        from wishlist.models import WishlistItem
        in_wishlist = WishlistItem.objects.filter(
            wishlist__user=request.user,
            product=product
        ).exists()
    
    context = {
        'product': product,
        'in_cart': in_cart,
        'in_wishlist': in_wishlist,
        'colors': colors,
        'sizes': sizes,
        'has_variations': has_variations,
        'product_images': product_images,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'user_review': user_review,
        'user_can_review': user_can_review,
        'user_has_reviewed': user_has_reviewed,
        'similar_products': similar_products,
        'frequently_bought': frequently_bought,
    }
    return render(request, 'product_detail.html', context)


def search(request):
    keyword = request.GET.get('keyword', '').strip()
    product_count = 0
    
    if keyword:
        products = Product.objects.filter(
            Q(product_name__icontains=keyword) | Q(description__icontains=keyword),
            is_available=True
        ).distinct()
        products, filters, current_query_string, filters_applied, price_bounds = _apply_product_filters(request, products)
        product_count = products.count()

        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
    else:
        products = Product.objects.none()
        filters = {
            'min_price': '',
            'max_price': '',
            'sale_only': False,
            'in_stock': False,
            'sort': 'newest'
        }
        current_query_string = ''
        filters_applied = False
        price_bounds = _get_price_bounds()
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
        'current_filters': filters,
        'filters_applied': filters_applied,
        'current_query_string': current_query_string,
        'price_bounds': price_bounds,
    }
    return render(request, 'store/store.html', context)


def check_pincode(request):
    """Check pincode serviceability via AJAX"""
    if request.method == 'POST':
        pincode = request.POST.get('pincode', '').strip()
        
        if not pincode:
            return JsonResponse({'success': False, 'message': 'Please enter a pincode'})
        
        # Check in database first
        try:
            pincode_obj = Pincode.objects.get(pincode=pincode)
            return JsonResponse({
                'success': True,
                'serviceable': pincode_obj.is_serviceable,
                'city': pincode_obj.city,
                'state': pincode_obj.state,
                'delivery_days': pincode_obj.delivery_days,
                'cod_available': pincode_obj.cod_available,
                'message': f'Delivery available to {pincode_obj.city}, {pincode_obj.state}'
            })
        except Pincode.DoesNotExist:
            # Use utility function as fallback
            is_serviceable, message = check_pincode_serviceability(pincode)
            return JsonResponse({
                'success': True,
                'serviceable': is_serviceable,
                'message': message
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})
