from .models import Cart, CartItem

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def cart(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        cart_count = sum([item.quantity for item in cart_items])
    except Cart.DoesNotExist:
        cart_count = 0
    
    return dict(cart_count=cart_count)

