from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from cart.models import Cart, CartItem
from notifications.utils import send_email_notification, create_notification


@staff_member_required
def abandoned_carts_list(request):
    """List all abandoned carts"""
    abandoned_carts = Cart.objects.filter(
        is_abandoned=True
    ).select_related('user').prefetch_related('items')
    
    # Calculate totals for each cart
    carts_with_totals = []
    for cart in abandoned_carts:
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        total = sum(item.sub_total() for item in cart_items)
        carts_with_totals.append({
            'cart': cart,
            'item_count': cart_items.count(),
            'total': total,
            'items': cart_items
        })
    
    context = {
        'carts_with_totals': carts_with_totals,
        'total_abandoned': abandoned_carts.count(),
    }
    return render(request, 'admin/abandoned_carts.html', context)


@staff_member_required
def send_abandoned_cart_reminder(request, cart_id):
    """Manually send reminder for abandoned cart"""
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from notifications.utils import send_email_notification
    
    cart = get_object_or_404(Cart, id=cart_id, is_abandoned=True)
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    
    if not cart.user or not cart.user.email:
        messages.error(request, 'Cart has no associated user or email.')
        return redirect('admin:abandoned_carts_list')
    
    # Calculate total
    total = sum(item.sub_total() for item in cart_items)
    
    subject = "Complete Your Purchase - Items Waiting in Your Cart!"
    message = f"""
    Hi {cart.user.first_name or 'there'},
    
    We noticed you left some items in your cart. Don't miss out!
    
    Items in your cart:
    """
    for item in cart_items:
        message += f"\n- {item.product.product_name} (Qty: {item.quantity}) - ₹{item.sub_total()}"
    
    message += f"""
    
    Total: ₹{total:.2f}
    
    Complete your purchase now!
    
    Best regards,
    Aromas by HarNoor Team
    """
    
    if send_email_notification(cart.user.email, subject, message, 'abandoned_cart'):
        cart.reminder_count += 1
        cart.reminder_sent = True
        cart.save()
        messages.success(request, f'Reminder sent to {cart.user.email}')
    else:
        messages.error(request, 'Failed to send reminder email.')
    
    return redirect('admin:abandoned_carts_list')

