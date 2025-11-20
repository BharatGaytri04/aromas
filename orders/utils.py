from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from .models import Order, OrderProduct, Payment
import uuid
try:
    from xhtml2pdf import pisa
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


def generate_pdf_invoice(order):
    """Generate PDF invoice for order"""
    if not PDF_AVAILABLE:
        return None
    
    template_path = 'orders/invoice_pdf.html'
    from django.template import Context
    context = {'order': order}
    
    template = get_template(template_path)
    html = template.render(context)
    
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        return result.getvalue()
    return None


def send_invoice_email(order):
    """Send invoice PDF via email"""
    from notifications.utils import send_email_notification
    
    pdf_content = generate_pdf_invoice(order)
    if not pdf_content:
        return False
    
    # For now, send email with link to download
    # Full email with PDF attachment requires more setup
    subject = f'Invoice for Order #{order.order_number}'
    message = f"""
    Dear {order.full_name()},
    
    Please find your invoice for Order #{order.order_number} attached.
    
    You can also download it from your order history.
    
    Thank you for shopping with us!
    
    Best regards,
    Aromas by HarNoor Team
    """
    
    send_email_notification(order.email, subject, message, 'invoice')
    return True


def generate_order_number(user_id):
    """
    Generate a unique order number for a user.
    
    This is a utility wrapper around the model's static method.
    Format: YYYYMMDDHHMMSS + UserID (4 digits) + Random (4 digits)
    Example: 2024121514302500015678
    
    Args:
        user_id: The ID of the user placing the order
        
    Returns:
        str: A unique order number
    """
    return Order.generate_order_number(user_id)


def create_order_from_cart(user, cart_items, form_data, payment_method='COD', discount=0):
    """
    Create an order from cart items.
    
    This utility function handles the complete order creation process:
    - Validates stock availability
    - Creates payment record
    - Generates unique order number
    - Creates order with all details
    - Creates order products
    - Manages stock
    - Creates tracking entry
    - Sends notifications
    
    Args:
        user: The user placing the order
        cart_items: QuerySet of CartItem objects
        form_data: Cleaned form data from OrderForm
        payment_method: Payment method (default: 'COD')
        discount: Discount amount from coupon (default: 0)
        
    Returns:
        tuple: (order, success_message) or (None, error_message)
    """
    from store.models import Product
    
    # Validate stock availability
    insufficient_stock_items = []
    for cart_item in cart_items:
        if cart_item.product.stock < cart_item.quantity:
            insufficient_stock_items.append({
                'product': cart_item.product.product_name,
                'available': cart_item.product.stock,
                'requested': cart_item.quantity
            })
    
    if insufficient_stock_items:
        error_msg = "Some products don't have sufficient stock:\n"
        for item in insufficient_stock_items:
            error_msg += f"- {item['product']}: Available {item['available']}, Requested {item['requested']}\n"
        return None, error_msg
    
    # Calculate totals
    total = sum(cart_item.product.price * cart_item.quantity for cart_item in cart_items)
    tax = (2 * total) / 100  # 2% tax
    final_total = total - discount + tax
    
    # Create payment
    payment = Payment.objects.create(
        user=user,
        payment_id=str(uuid.uuid4()),
        payment_method=payment_method,
        amount_paid=str(final_total),
        status='Pending' if payment_method == 'COD' else 'Completed'
    )
    
    # Generate unique order number
    order_number = generate_order_number(user.id)
    
    # Create order
    order = Order.objects.create(
        user=user,
        payment=payment,
        order_number=order_number,
        first_name=form_data['first_name'],
        last_name=form_data['last_name'],
        phone=form_data['phone'],
        email=form_data['email'],
        address_line_1=form_data['address_line_1'],
        address_line_2=form_data.get('address_line_2', ''),
        city=form_data['city'],
        state=form_data['state'],
        country=form_data['country'],
        pincode=form_data.get('pincode', ''),
        order_note=form_data.get('order_note', ''),
        order_total=total,
        tax=tax,
        discount=discount,
        final_total=final_total,
        status='New',
        is_ordered=True
    )
    
    # Create order products and manage stock
    for cart_item in cart_items:
        order_product = OrderProduct.objects.create(
            order=order,
            payment=payment,
            user=user,
            product=cart_item.product,
            quantity=cart_item.quantity,
            product_price=cart_item.product.price,
            ordered=True
        )
        # Add variations
        variations = cart_item.variations.all()
        if variations:
            order_product.variations.set(variations)
        
        # Reduce product stock and update availability
        product = cart_item.product
        product.stock -= cart_item.quantity
        
        # Update product availability if stock reaches 0
        if product.stock <= 0:
            product.is_available = False
            product.stock = 0  # Ensure stock doesn't go negative
        
        product.save()
    
    # Create order tracking entry
    from .models import OrderTracking
    OrderTracking.objects.create(
        order=order,
        status='New',
        description='Order placed successfully'
    )
    
    # Send notifications
    try:
        from notifications.utils import notify_new_order
        notify_new_order(order)
    except Exception as e:
        # Don't fail order if notification fails
        pass
    
    # Send invoice email
    try:
        send_invoice_email(order)
    except Exception as e:
        # Don't fail order if email fails
        pass
    
    success_message = f'Order placed successfully! Your order number is {order_number}'
    return order, success_message

