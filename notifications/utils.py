from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, EmailNotification
from orders.models import Order


def create_notification(user=None, notification_type='new_order', title='', message='', 
                       order=None, is_admin_notification=False):
    """Create a notification"""
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        order=order,
        is_admin_notification=is_admin_notification
    )
    return notification


def send_email_notification(recipient_email, subject, message, notification_type='general'):
    """Send email notification"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else settings.EMAIL_HOST_USER,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        
        # Record email notification
        EmailNotification.objects.create(
            recipient_email=recipient_email,
            subject=subject,
            message=message,
            notification_type=notification_type,
            is_sent=True
        )
        return True
    except Exception as e:
        # Record failed email
        EmailNotification.objects.create(
            recipient_email=recipient_email,
            subject=subject,
            message=message,
            notification_type=notification_type,
            is_sent=False,
            error_message=str(e)
        )
        return False


def notify_new_order(order):
    """Notify admin about new order"""
    # Create admin notification
    create_notification(
        notification_type='new_order',
        title=f'New Order #{order.order_number}',
        message=f'New order received from {order.full_name()} for ₹{order.final_total:.2f}',
        order=order,
        is_admin_notification=True
    )
    
    # Send email to admin (if configured)
    if hasattr(settings, 'ADMIN_EMAIL'):
        email_subject = f'New Order #{order.order_number}'
        email_message = f"""
        New order has been received!
        
        Order Number: {order.order_number}
        Customer: {order.full_name()}
        Email: {order.email}
        Phone: {order.phone}
        Total Amount: ₹{order.final_total:.2f}
        
        Please check the admin panel for details.
        """
        send_email_notification(
            settings.ADMIN_EMAIL,
            email_subject,
            email_message,
            'new_order'
        )
    
    # Send email to customer
    customer_email_subject = f'Order Confirmation - #{order.order_number}'
    customer_email_message = f"""
    Thank you for your order!
    
    Your order #{order.order_number} has been received and is being processed.
    
    Order Details:
    - Order Number: {order.order_number}
    - Total Amount: ₹{order.final_total:.2f}
    - Payment Method: {order.payment.get_payment_method_display() if order.payment else 'N/A'}
    
    We will send you updates on your order status.
    
    Thank you for shopping with us!
    """
    send_email_notification(
        order.email,
        customer_email_subject,
        customer_email_message,
        'order_confirmation'
    )


def notify_low_stock(product):
    """Notify admin about low stock"""
    create_notification(
        notification_type='low_stock',
        title=f'Low Stock Alert - {product.product_name}',
        message=f'Product "{product.product_name}" stock is low ({product.stock} units remaining)',
        is_admin_notification=True
    )
    
    # Send email if configured
    if hasattr(settings, 'ADMIN_EMAIL'):
        email_subject = f'Low Stock Alert - {product.product_name}'
        email_message = f"""
        Product Stock Alert!
        
        Product: {product.product_name}
        Current Stock: {product.stock} units
        Alert Threshold: {product.min_stock_alert} units
        
        Please restock this product soon.
        """
        send_email_notification(
            settings.ADMIN_EMAIL,
            email_subject,
            email_message,
            'low_stock'
        )

