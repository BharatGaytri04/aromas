from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import csv
from .models import Order, OrderProduct, Payment
from store.models import Product
from notifications.models import Notification


@staff_member_required
def admin_dashboard(request):
    """Admin sales dashboard with analytics"""
    
    # Date ranges
    today = timezone.now().date()
    this_week = today - timedelta(days=7)
    this_month = today - timedelta(days=30)
    this_year = today - timedelta(days=365)
    
    # Order statistics
    total_orders = Order.objects.filter(is_ordered=True).count()
    today_orders = Order.objects.filter(is_ordered=True, created_at__date=today).count()
    week_orders = Order.objects.filter(is_ordered=True, created_at__date__gte=this_week).count()
    month_orders = Order.objects.filter(is_ordered=True, created_at__date__gte=this_month).count()
    
    # Revenue statistics
    total_revenue = Order.objects.filter(is_ordered=True).aggregate(
        total=Sum('final_total')
    )['total'] or 0
    
    today_revenue = Order.objects.filter(
        is_ordered=True, 
        created_at__date=today
    ).aggregate(total=Sum('final_total'))['total'] or 0
    
    week_revenue = Order.objects.filter(
        is_ordered=True,
        created_at__date__gte=this_week
    ).aggregate(total=Sum('final_total'))['total'] or 0
    
    month_revenue = Order.objects.filter(
        is_ordered=True,
        created_at__date__gte=this_month
    ).aggregate(total=Sum('final_total'))['total'] or 0
    
    # Order status breakdown
    status_breakdown = Order.objects.filter(is_ordered=True).values('status').annotate(
        count=Count('id')
    )
    
    # Recent orders
    recent_orders = Order.objects.filter(is_ordered=True).order_by('-created_at')[:10]
    
    # Top selling products
    top_products = OrderProduct.objects.values('product__product_name').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('product_price')
    ).order_by('-total_sold')[:10]
    
    # Low stock alerts
    from django.db.models import F
    low_stock_products = Product.objects.filter(
        stock__lte=F('min_stock_alert'),
        is_available=True
    )[:10]
    
    # Unread notifications
    unread_notifications = Notification.objects.filter(
        is_admin_notification=True,
        is_read=False
    ).order_by('-created_at')[:10]
    
    # Pending returns
    from orders.models import ReturnRequest
    pending_returns = ReturnRequest.objects.filter(status='pending').count()
    
    # Abandoned carts
    from cart.models import Cart
    abandoned_carts = Cart.objects.filter(is_abandoned=True).count()
    
    context = {
        'total_orders': total_orders,
        'today_orders': today_orders,
        'week_orders': week_orders,
        'month_orders': month_orders,
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'week_revenue': week_revenue,
        'month_revenue': month_revenue,
        'status_breakdown': status_breakdown,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'low_stock_products': low_stock_products,
        'unread_notifications': unread_notifications,
        'pending_returns': pending_returns,
        'abandoned_carts': abandoned_carts,
    }
    
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
def export_orders_csv(request):
    """Export orders to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Order Number', 'Customer Name', 'Email', 'Phone', 'Status',
        'Order Total', 'Tax', 'Discount', 'Final Total', 'Payment Method',
        'Created At', 'City', 'State', 'Pincode'
    ])
    
    orders = Order.objects.filter(is_ordered=True).order_by('-created_at')
    
    for order in orders:
        writer.writerow([
            order.order_number,
            order.full_name(),
            order.email,
            order.phone,
            order.status,
            order.order_total,
            order.tax,
            order.discount,
            order.final_total,
            order.payment.get_payment_method_display() if order.payment else 'N/A',
            order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            order.city,
            order.state,
            order.pincode,
        ])
    
    return response


@staff_member_required
def get_new_orders_count(request):
    """Get count of new unread orders for popup"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        new_orders_count = Notification.objects.filter(
            is_admin_notification=True,
            is_read=False,
            notification_type='new_order'
        ).count()
        
        return JsonResponse({
            'count': new_orders_count,
            'has_new': new_orders_count > 0
        })
    return JsonResponse({'error': 'Invalid request'})

