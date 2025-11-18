from django.shortcuts import render, get_object_or_404, redirect
from .models import Cart, CartItem
from store.models import Product, Variation

# Create your views here.



def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    
    # Check if product is available and in stock
    if not product.is_available or product.stock <= 0:
        return redirect('product_detail', product_slug=product.slug)
    
    # If product has variations, ensure selection happens via POST
    if product.variation_set.filter(is_active=True).exists() and request.method != 'POST':
        return redirect('product_detail', product_slug=product.slug)
    
    product_variation_objs = []
    product_variation_ids = []
    if request.method == 'POST':
        variation_keys = [key for key in request.POST.keys() if key not in ['csrfmiddlewaretoken', 'quantity']]
        for key in variation_keys:
            value = request.POST.get(key)
            if value:
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value, is_active=True)
                    product_variation_objs.append(variation)
                    product_variation_ids.append(variation.id)
                except Variation.DoesNotExist:
                    pass
        product_variation_ids.sort()
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
        cart.save()
    
    cart_item = None
    existing_variation_lists = []
    ids = []
    cart_items = CartItem.objects.filter(product=product, cart=cart, is_active=True)
    if cart_items.exists():
        for item in cart_items:
            variations = list(item.variations.all())
            variation_ids = sorted([var.id for var in variations])
            existing_variation_lists.append(variation_ids)
            ids.append(item.id)
        if product_variation_ids in existing_variation_lists:
            index = existing_variation_lists.index(product_variation_ids)
            item_id = ids[index]
            cart_item = CartItem.objects.get(id=item_id)
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
        else:
            cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
            if product_variation_objs:
                cart_item.variations.set(product_variation_objs)
            cart_item.save()
    else:
        cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
        if product_variation_objs:
            cart_item.variations.set(product_variation_objs)
        cart_item.save()

    return redirect('cart')




def cart(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        total = 0
        quantity = 0
        tax = 0
        grand_total = 0
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        tax = (2 * total) / 100  # 2% tax
        grand_total = total + tax
    except Cart.DoesNotExist:
        cart_items = []
        total = 0
        quantity = 0
        tax = 0
        grand_total = 0
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)


def remove_cart(request, product_id, cart_item_id):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        cart_item.delete()
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        pass
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        pass
    return redirect('cart')