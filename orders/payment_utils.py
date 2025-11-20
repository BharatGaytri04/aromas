"""
Payment utilities for handling Razorpay payments.
This module will be activated when Razorpay keys are added to settings.
"""
from django.conf import settings
from django.http import JsonResponse
from .models import Order, Payment
import json


def is_razorpay_enabled():
    """Check if Razorpay is enabled in settings"""
    return getattr(settings, 'RAZORPAY_ENABLED', False)


def create_razorpay_order(order):
    """
    Create a Razorpay order for payment.
    
    This function will be called when customer selects Razorpay payment.
    It creates an order on Razorpay's server and returns order details.
    
    Args:
        order: Order object
        
    Returns:
        dict: Razorpay order details with order_id and amount
    """
    if not is_razorpay_enabled():
        return None
    
    try:
        import razorpay
        
        # Initialize Razorpay client
        razorpay_client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        
        # Create order on Razorpay
        # Amount should be in paise (smallest currency unit)
        # For INR: 1 rupee = 100 paise
        amount_in_paise = int(order.final_total * 100)
        
        razorpay_order = razorpay_client.order.create({
            'amount': amount_in_paise,  # Amount in paise
            'currency': getattr(settings, 'RAZORPAY_CURRENCY', 'INR'),
            'receipt': order.order_number,
            'notes': {
                'order_number': order.order_number,
                'customer_name': order.full_name(),
                'customer_email': order.email,
            }
        })
        
        return {
            'order_id': razorpay_order['id'],
            'amount': amount_in_paise,
            'currency': razorpay_order['currency'],
            'key_id': settings.RAZORPAY_KEY_ID,
        }
    except ImportError:
        # Razorpay package not installed
        return None
    except Exception as e:
        # Log error in production
        print(f"Razorpay order creation error: {str(e)}")
        return None


def verify_razorpay_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """
    Verify Razorpay payment signature.
    
    This function verifies that the payment was actually made on Razorpay
    and not tampered with.
    
    Args:
        razorpay_order_id: Order ID from Razorpay
        razorpay_payment_id: Payment ID from Razorpay
        razorpay_signature: Signature from Razorpay
        
    Returns:
        bool: True if payment is verified, False otherwise
    """
    if not is_razorpay_enabled():
        return False
    
    try:
        import razorpay
        
        # Initialize Razorpay client
        razorpay_client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        
        # Verify payment signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        # This will raise an exception if signature is invalid
        razorpay_client.utility.verify_payment_signature(params_dict)
        
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"Razorpay payment verification error: {str(e)}")
        return False


def update_payment_status(order, razorpay_payment_id, status='Completed'):
    """
    Update payment status after Razorpay payment is verified.
    
    Args:
        order: Order object
        razorpay_payment_id: Payment ID from Razorpay
        status: Payment status ('Completed' or 'Failed')
    """
    try:
        payment = order.payment
        if payment:
            payment.payment_id = razorpay_payment_id
            payment.status = status
            payment.save()
            
            # Update order status
            if status == 'Completed':
                order.is_ordered = True
                order.save()
            
            return True
    except Exception as e:
        print(f"Error updating payment status: {str(e)}")
        return False

