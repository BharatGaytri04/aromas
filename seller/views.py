from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from orders.models import Order, OrderProduct, OrderTracking
from notifications.utils import create_notification


@staff_member_required
def seller_dashboard(request):
    """Seller dashboard to view and manage all orders"""
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    date_filter = request.GET.get('date', '')
    
    # Start with all ordered orders
    orders = Order.objects.filter(is_ordered=True).order_by('-created_at')
    
    # Apply status filter
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Apply search filter
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Apply date filter
    if date_filter == 'today':
        today = timezone.now().date()
        orders = orders.filter(created_at__date=today)
    elif date_filter == 'week':
        week_ago = timezone.now().date() - timedelta(days=7)
        orders = orders.filter(created_at__date__gte=week_ago)
    elif date_filter == 'month':
        month_ago = timezone.now().date() - timedelta(days=30)
        orders = orders.filter(created_at__date__gte=month_ago)
    
    # Get order statistics
    total_orders = Order.objects.filter(is_ordered=True).count()
    new_orders = Order.objects.filter(is_ordered=True, status='New').count()
    in_process_orders = Order.objects.filter(
        is_ordered=True, 
        status__in=['Accepted', 'Packed']
    ).count()
    ready_to_ship = Order.objects.filter(
        is_ordered=True, 
        status='Packed'
    ).count()
    shipped_orders = Order.objects.filter(
        is_ordered=True, 
        status__in=['Shipped', 'Out for Delivery']
    ).count()
    completed_orders = Order.objects.filter(
        is_ordered=True, 
        status__in=['Delivered', 'Completed']
    ).count()
    
    # Get status counts for filter badges
    status_counts = Order.objects.filter(is_ordered=True).values('status').annotate(
        count=Count('id')
    )
    status_count_dict = {item['status']: item['count'] for item in status_counts}
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'search_query': search_query,
        'date_filter': date_filter,
        'total_orders': total_orders,
        'new_orders': new_orders,
        'in_process_orders': in_process_orders,
        'ready_to_ship': ready_to_ship,
        'shipped_orders': shipped_orders,
        'completed_orders': completed_orders,
        'status_counts': status_count_dict,
        'status_choices': Order.STATUS,
    }
    
    return render(request, 'seller/dashboard.html', context)


@staff_member_required
def update_order_status(request, order_number):
    """Update order status via AJAX"""
    if request.method == 'POST':
        try:
            order = get_object_or_404(Order, order_number=order_number, is_ordered=True)
            new_status = request.POST.get('status')
            
            if not new_status:
                return JsonResponse({
                    'success': False,
                    'message': 'Status is required.'
                })
            
            # Validate status
            valid_statuses = [choice[0] for choice in Order.STATUS]
            if new_status not in valid_statuses:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid status.'
                })
            
            old_status = order.status
            order.status = new_status
            
            # Update tracking timestamps
            if new_status == 'Shipped' and not order.shipped_at:
                order.shipped_at = timezone.now()
            elif new_status in ['Delivered', 'Completed'] and not order.delivered_at:
                order.delivered_at = timezone.now()
            
            order.save()
            
            # Create tracking entry
            OrderTracking.objects.create(
                order=order,
                status=new_status,
                description=f'Status changed from {old_status} to {new_status}'
            )
            
            # Notify customer if status changed to important states
            if new_status in ['Shipped', 'Delivered', 'Completed']:
                try:
                    create_notification(
                        notification_type='order_update',
                        title=f'Order #{order.order_number} Update',
                        message=f'Your order status has been updated to {new_status}',
                        order=order,
                        user=order.user
                    )
                except:
                    pass
            
            return JsonResponse({
                'success': True,
                'message': f'Order status updated to {new_status}',
                'new_status': new_status,
                'status_display': dict(Order.STATUS)[new_status]
            })
            
        except Order.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Order not found.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    })


@staff_member_required
def seller_order_detail(request, order_number):
    """Seller view of order details"""
    try:
        order = get_object_or_404(Order, order_number=order_number, is_ordered=True)
        order_products = OrderProduct.objects.filter(order=order)
        tracking_history = OrderTracking.objects.filter(order=order).order_by('-created_at')
        timeline = order.get_status_timeline()
        
        context = {
            'order': order,
            'order_products': order_products,
            'tracking_history': tracking_history,
            'timeline': timeline,
            'is_seller_view': True,
            'status_choices': Order.STATUS,
        }
        return render(request, 'seller/order_detail.html', context)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('seller:dashboard')
