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
    import logging
    logger = logging.getLogger(__name__)
    
    if not is_razorpay_enabled():
        logger.error("Razorpay is not enabled in settings")
        return None
    
    # Validate API keys before proceeding
    key_id = getattr(settings, 'RAZORPAY_KEY_ID', '').strip()
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '').strip()
    
    if not key_id:
        logger.error("RAZORPAY_KEY_ID is not set or is empty")
        raise ValueError("RAZORPAY_KEY_ID is not configured. Please check your .env file.")
    
    if not key_secret:
        logger.error("RAZORPAY_KEY_SECRET is not set or is empty")
        raise ValueError("RAZORPAY_KEY_SECRET is not configured. Please check your .env file.")
    
    # Check for extra spaces (common issue)
    if key_id != key_id.strip() or key_secret != key_secret.strip():
        logger.warning("Razorpay keys may have extra spaces. Trimming...")
        key_id = key_id.strip()
        key_secret = key_secret.strip()
    
    try:
        import razorpay
    except ImportError:
        logger.error("Razorpay package is not installed. Run: pip install razorpay")
        raise ImportError("Razorpay package is not installed. Please install it: pip install razorpay")
    
    try:
        # Initialize Razorpay client with validated keys
        logger.info(f"Initializing Razorpay client with Key ID: {key_id[:10]}...")
        razorpay_client = razorpay.Client(auth=(key_id, key_secret))
        
        # Validate order amount
        if not order.final_total or order.final_total <= 0:
            logger.error(f"Invalid order amount: {order.final_total}")
            raise ValueError(f"Invalid order amount: {order.final_total}")
        
        # Create order on Razorpay
        # Amount should be in paise (smallest currency unit)
        # For INR: 1 rupee = 100 paise
        amount_in_paise = int(order.final_total * 100)
        
        if amount_in_paise < 100:  # Minimum 1 rupee
            logger.error(f"Order amount too small: {amount_in_paise} paise")
            raise ValueError("Order amount must be at least ₹1.00")
        
        order_data = {
            'amount': amount_in_paise,  # Amount in paise
            'currency': getattr(settings, 'RAZORPAY_CURRENCY', 'INR'),
            'receipt': order.order_number,
            'notes': {
                'order_number': order.order_number,
                'customer_name': order.full_name(),
                'customer_email': order.email,
            }
        }
        
        logger.info(f"Creating Razorpay order for {amount_in_paise} paise (Order: {order.order_number})")
        
        # Create order with detailed error handling
        try:
            razorpay_order = razorpay_client.order.create(order_data)
            logger.info(f"Razorpay order created successfully: {razorpay_order.get('id')}")
        except razorpay.errors.BadRequestError as e:
            logger.error(f"Razorpay BadRequestError: {str(e)}")
            raise ValueError(f"Invalid request to Razorpay: {str(e)}")
        except razorpay.errors.ServerError as e:
            logger.error(f"Razorpay ServerError: {str(e)}")
            raise ConnectionError(f"Razorpay server error. Please try again later: {str(e)}")
        except razorpay.errors.GatewayError as e:
            logger.error(f"Razorpay GatewayError: {str(e)}")
            raise ConnectionError(f"Payment gateway error. Please check your internet connection: {str(e)}")
        except Exception as e:
            logger.error(f"Razorpay API error: {type(e).__name__}: {str(e)}")
            raise ConnectionError(f"Failed to connect to Razorpay: {str(e)}")
        
        return {
            'order_id': razorpay_order['id'],
            'amount': amount_in_paise,
            'currency': razorpay_order['currency'],
            'key_id': key_id,
        }
    except AttributeError as e:
        logger.error(f"Razorpay settings error: {str(e)}")
        raise ValueError(f"Razorpay configuration error: {str(e)}")
    except (ValueError, ConnectionError) as e:
        # Re-raise validation and connection errors
        raise
    except Exception as e:
        # Catch any other unexpected errors
        logger.error(f"Unexpected Razorpay error: {type(e).__name__}: {str(e)}")
        raise Exception(f"Failed to create payment order: {str(e)}")


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

