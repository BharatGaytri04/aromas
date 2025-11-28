from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Order, OrderProduct, OrderTracking, ReturnRequest
from .utils import generate_pdf_invoice
from .payment_utils import is_razorpay_enabled, create_razorpay_order, verify_razorpay_payment, update_payment_status
from notifications.utils import create_notification, send_email_notification
import json


@login_required(login_url='accounts:login')
def order_success(request, order_number):
    """Display order success page after order placement"""
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
        order_products = OrderProduct.objects.filter(order=order)
        
        context = {
            'order': order,
            'order_products': order_products,
        }
        return render(request, 'orders/order_success.html', context)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('store')


@login_required(login_url='accounts:login')
def order_detail(request, order_number):
    """View order details with tracking"""
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
        order_products = OrderProduct.objects.filter(order=order)
        tracking_history = OrderTracking.objects.filter(order=order)
        timeline = order.get_status_timeline()
        
        context = {
            'order': order,
            'order_products': order_products,
            'tracking_history': tracking_history,
            'timeline': timeline,
        }
        return render(request, 'orders/order_detail.html', context)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('accounts:dashboard')


@login_required(login_url='accounts:login')
def order_list(request):
    """List all user orders"""
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_list.html', context)


@login_required(login_url='accounts:login')
def download_invoice(request, order_number):
    """Download PDF invoice"""
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
        pdf = generate_pdf_invoice(order)
        
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_number}.pdf"'
            return response
        else:
            messages.error(request, 'Error generating invoice.')
            return redirect('orders:order_detail', order_number=order_number)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('accounts:dashboard')


@login_required(login_url='accounts:login')
def request_return(request, order_number):
    """Request return/refund for order"""
    if request.method == 'POST':
        try:
            order = Order.objects.get(order_number=order_number, user=request.user)
            reason = request.POST.get('reason')
            order_product_id = request.POST.get('order_product_id')
            
            if not reason:
                messages.error(request, 'Please provide a reason for return.')
                return redirect('orders:order_detail', order_number=order_number)
            
            order_product = None
            if order_product_id:
                order_product = get_object_or_404(OrderProduct, id=order_product_id, order=order)
            
            return_request = ReturnRequest.objects.create(
                order=order,
                order_product=order_product,
                user=request.user,
                reason=reason,
                status='pending'
            )
            
            # Notify admin
            create_notification(
                notification_type='refund_request',
                title=f'Return Request for Order #{order.order_number}',
                message=f'Customer {request.user.email} requested return for order {order.order_number}',
                order=order,
                is_admin_notification=True
            )
            
            messages.success(request, 'Return request submitted successfully. We will review it soon.')
            return redirect('orders:order_detail', order_number=order_number)
        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')
            return redirect('accounts:dashboard')
    
    return redirect('accounts:dashboard')


@login_required(login_url='accounts:login')
def create_razorpay_payment(request, order_number):
    """
    Create Razorpay payment order and return payment details.
    Called via AJAX when customer selects Razorpay payment.
    """
    if not is_razorpay_enabled():
        return JsonResponse({
            'success': False,
            'message': 'Online payment is currently unavailable. Please contact support.'
        })
    
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
        
        # Create Razorpay order
        try:
            razorpay_order = create_razorpay_order(order)
        except Exception as e:
            # Log the actual error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Razorpay order creation failed: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Payment initialization failed: {str(e)}. Please try again.'
            })
        
        if razorpay_order:
            return JsonResponse({
                'success': True,
                'order_id': razorpay_order['order_id'],
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency'],
                'key_id': razorpay_order['key_id'],
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Failed to create payment order. Please check your internet connection and try again.'
            })
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Order not found.'
        })
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in create_razorpay_payment: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@csrf_exempt
def razorpay_payment_callback(request):
    """
    Handle Razorpay payment callback after payment is completed.
    This is called by Razorpay after payment is made.
    """
    if request.method == 'POST':
        try:
            # Get payment details from Razorpay
            razorpay_order_id = request.POST.get('razorpay_order_id')
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_signature = request.POST.get('razorpay_signature')
            order_number = request.POST.get('order_number')
            
            if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature, order_number]):
                return JsonResponse({
                    'success': False,
                    'message': 'Missing payment details.'
                })
            
            # Get order
            try:
                order = Order.objects.get(order_number=order_number)
            except Order.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Order not found.'
                })
            
            # Verify payment signature
            if verify_razorpay_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
                # Update payment status (this also sets is_ordered=True)
                update_payment_status(order, razorpay_payment_id, status='Completed')
                
                # Finalize order (cart is already cleared in checkout)
                order.is_ordered = True
                order.status = 'New'
                order.save()
                
                # Create order tracking entry
                OrderTracking.objects.create(
                    order=order,
                    status='New',
                    description='Payment completed via Razorpay'
                )
                
                # Send notifications
                try:
                    from notifications.utils import notify_new_order
                    notify_new_order(order)
                except:
                    pass
                
                # Send invoice email
                try:
                    from orders.utils import send_invoice_email
                    send_invoice_email(order)
                except:
                    pass
                
                return JsonResponse({
                    'success': True,
                    'message': 'Payment successful!',
                    'redirect_url': f'/orders/order-success/{order_number}/'
                })
            else:
                # Payment verification failed
                update_payment_status(order, razorpay_payment_id, status='Failed')
                return JsonResponse({
                    'success': False,
                    'message': 'Payment verification failed.'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error processing payment: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    })
