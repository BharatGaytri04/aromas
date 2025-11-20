from .models import Product
from orders.models import OrderProduct


def get_similar_products(product, limit=4):
    """Get similar products based on category"""
    similar_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:limit]
    return similar_products


def get_frequently_bought_together(product, limit=4):
    """Get products frequently bought together"""
    # Get orders that contain this product
    orders_with_product = OrderProduct.objects.filter(
        product=product
    ).values_list('order_id', flat=True).distinct()
    
    # Get other products from those orders
    from django.db.models import Count
    frequently_bought = OrderProduct.objects.filter(
        order_id__in=orders_with_product
    ).exclude(product=product).values('product').annotate(
        count=Count('product')
    ).order_by('-count')[:limit]
    
    product_ids = [item['product'] for item in frequently_bought]
    products = Product.objects.filter(
        id__in=product_ids,
        is_available=True
    )
    
    # Return in order of frequency
    product_dict = {p.id: p for p in products}
    return [product_dict[pid] for pid in product_ids if pid in product_dict]


def check_pincode_serviceability(pincode):
    """
    Check if pincode is serviceable
    This is a basic implementation - you can integrate with shipping APIs
    """
    # Basic validation - 6 digits
    if not pincode or len(pincode) != 6 or not pincode.isdigit():
        return False, "Invalid pincode format"
    
    # You can add a Pincode model or API integration here
    # For now, we'll assume all 6-digit pincodes are serviceable
    # You can create a Pincode model with serviceable pincodes
    
    return True, "Serviceable"

