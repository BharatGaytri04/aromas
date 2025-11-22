from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from orders.forms import OrderForm
from orders.models import Order, OrderProduct, Payment
from store.models import Product, Variation
import uuid
import datetime

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
        messages.warning(request, f'{product.product_name} is currently out of stock.')
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
            # Check if we can add more to cart
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.warning(request, f'Only {product.stock} units of {product.product_name} are available. You already have {cart_item.quantity} in your cart.')
        else:
            # Check stock before adding new item
            if product.stock > 0:
                cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
                if product_variation_objs:
                    cart_item.variations.set(product_variation_objs)
                cart_item.save()
            else:
                messages.warning(request, f'{product.product_name} is out of stock.')
    else:
        # Check stock before adding new item
        if product.stock > 0:
            cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
            if product_variation_objs:
                cart_item.variations.set(product_variation_objs)
            cart_item.save()
        else:
            messages.warning(request, f'{product.product_name} is out of stock.')

    return redirect('cart')




def cart(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        # Remove items from cart if product is no longer available or out of stock
        items_to_remove = []
        for cart_item in cart_items:
            product = cart_item.product
            # Remove if product is unavailable or out of stock
            if not product.is_available or product.stock <= 0:
                items_to_remove.append(cart_item)
            # Adjust quantity if requested quantity exceeds available stock
            elif cart_item.quantity > product.stock:
                cart_item.quantity = product.stock
                cart_item.save()
                if cart_item.quantity <= 0:
                    items_to_remove.append(cart_item)
        
        # Remove unavailable items
        for item in items_to_remove:
            item.delete()
        
        # Refresh cart items after cleanup
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        total = 0
        quantity = 0
        tax = 0
        grand_total = 0
        
        for cart_item in cart_items:
            item_total = cart_item.product.price * cart_item.quantity
            total += item_total
            quantity += cart_item.quantity
            # Calculate tax based on product-specific GST percentage
            gst_percentage = float(cart_item.product.gst_percentage)
            tax += (item_total * gst_percentage) / 100
        
        grand_total = total + tax
        
        # Show message if items were removed
        if items_to_remove:
            messages.warning(request, 'Some items were removed from your cart because they are no longer available or out of stock.')
    except Cart.DoesNotExist:
        cart_items = []
        total = 0
        quantity = 0
        tax = 0
        grand_total = 0
    
    # Get applied coupon if any
    applied_coupon = None
    discount = 0
    if request.user.is_authenticated and 'applied_coupon' in request.session:
        try:
            from coupons.models import Coupon
            coupon_id = request.session.get('applied_coupon')
            applied_coupon = Coupon.objects.get(id=coupon_id)
            discount = request.session.get('coupon_discount', 0)
        except:
            pass
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'discount': discount,
        'grand_total': grand_total,
        'applied_coupon': applied_coupon,
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


def checkout(request):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        # Redirect to login with next parameter
        from django.urls import reverse
        login_url = reverse('accounts:login')
        next_url = request.path
        return redirect(f"{login_url}?next={next_url}")
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        if not cart_items.exists():
            messages.warning(request, 'Your cart is empty. Please add items to your cart before checkout.')
            return redirect('cart')
        
        total = 0
        quantity = 0
        tax = 0
        grand_total = 0
        
        for cart_item in cart_items:
            item_total = cart_item.product.price * cart_item.quantity
            total += item_total
            quantity += cart_item.quantity
            # Calculate tax based on product-specific GST percentage
            gst_percentage = float(cart_item.product.gst_percentage)
            tax += (item_total * gst_percentage) / 100
        
        grand_total = total + tax
        
    except Cart.DoesNotExist:
        messages.warning(request, 'Your cart is empty. Please add items to your cart before checkout.')
        return redirect('cart')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            address_choice = request.POST.get('address_choice', 'new')
            saved_address_available = all([
                request.user.address_line_1,
                request.user.city,
                request.user.state,
                request.user.country,
                request.user.pincode,
            ])
            # ============================================================
            # STEP 2: System Checks the Cart
            # ============================================================
            # Validate stock availability before creating order
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
                messages.error(request, error_msg)
                return redirect('cart')
            
            # ============================================================
            # STEP 3: System Calculates Prices
            # ============================================================
            # Get payment method
            payment_method = request.POST.get('payment_method', 'COD')
            
            # Get coupon discount
            discount = 0
            applied_coupon = None
            if 'applied_coupon' in request.session:
                try:
                    from coupons.models import Coupon
                    coupon_id = request.session.get('applied_coupon')
                    applied_coupon = Coupon.objects.get(id=coupon_id)
                    discount = request.session.get('coupon_discount', 0)
                except:
                    pass
            
            # Recalculate with discount (Subtotal - Discount + Tax)
            final_total = total - discount + tax
            
            # ============================================================
            # STEP 6: A Payment Record is Created
            # ============================================================
            # Create payment record (even for COD)
            payment = Payment.objects.create(
                user=request.user,
                payment_id=str(uuid.uuid4()),
                payment_method=payment_method,
                amount_paid=str(final_total),
                status='Pending' if payment_method == 'COD' else 'Completed'
            )
            
            # ============================================================
            # STEP 5: A Unique Order Number is Generated
            # ============================================================
            # Generate unique order number (Format: YYYYMMDD-XXXXXX-XX)
            order_number = Order.generate_order_number(request.user.id)
            
            if address_choice == 'saved' and saved_address_available:
                address_line_1 = request.user.address_line_1
                address_line_2 = request.user.address_line_2 or ''
                city = request.user.city
                state = request.user.state
                country = request.user.country
                pincode = request.user.pincode or ''
            else:
                address_line_1 = form.cleaned_data['address_line_1']
                address_line_2 = form.cleaned_data.get('address_line_2', '')
                city = form.cleaned_data['city']
                state = form.cleaned_data['state']
                country = form.cleaned_data['country']
                pincode = form.cleaned_data.get('pincode', '')
            
            # ============================================================
            # STEP 4: An Order is Created (But Not Completed Yet)
            # ============================================================
            # Create order record with all customer and order details
            # Initially: is_ordered=False, status='New'
            order = Order.objects.create(
                user=request.user,
                payment=payment,
                order_number=order_number,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data['email'],
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                city=city,
                state=state,
                country=country,
                pincode=pincode,
                order_note=form.cleaned_data.get('order_note', ''),
                order_total=total,
                tax=tax,
                discount=discount,
                final_total=final_total,
                status='New',
                ip=request.META.get('REMOTE_ADDR'),
                is_ordered=False  # Will be set to True after all steps complete
            )
            
            # Record coupon usage if applied
            if applied_coupon:
                from coupons.models import CouponUsage
                CouponUsage.objects.create(
                    coupon=applied_coupon,
                    user=request.user,
                    order=order,
                    discount_amount=discount
                )
                applied_coupon.used_count += 1
                applied_coupon.save()
                
                # Clear coupon from session
                del request.session['applied_coupon']
                del request.session['coupon_discount']
            
            # ============================================================
            # STEP 7: Order Products are Saved
            # ============================================================
            # Create order products and manage stock
            for cart_item in cart_items:
                # ============================================================
                # STEP 8: Stock is Reduced (with double-check validation)
                # ============================================================
                # Use select_for_update to lock the product row and prevent race conditions
                # This ensures only one order can reduce stock at a time
                from django.db import transaction
                
                with transaction.atomic():
                    # Lock the product row for update (prevents concurrent modifications)
                    product = Product.objects.select_for_update().get(id=cart_item.product.id)
                    
                    # Double-check stock availability (in case it changed since initial validation)
                    if product.stock < cart_item.quantity:
                        # Stock insufficient - rollback transaction
                        messages.error(
                            request, 
                            f'Sorry, {product.product_name} is now out of stock. '
                            f'Only {product.stock} units available.'
                        )
                        # Delete the order and payment if stock is insufficient
                        order.delete()
                        payment.delete()
                        return redirect('cart')
                    
                    # Create OrderProduct record for each cart item
                    order_product = OrderProduct.objects.create(
                        order=order,
                        payment=payment,
                        user=request.user,
                        product=product,
                        quantity=cart_item.quantity,
                        product_price=product.price,
                        ordered=True
                    )
                    # Add product variations (color, size, etc.)
                    variations = cart_item.variations.all()
                    if variations:
                        order_product.variations.set(variations)
                    
                    # Reduce product stock
                    product.stock -= cart_item.quantity
                    
                    # Update product availability if stock reaches 0
                    if product.stock <= 0:
                        product.is_available = False
                        product.stock = 0  # Ensure stock doesn't go negative
                    
                    # Save product with updated stock
                    product.save()
                    
                    # Check if stock is low and send notification
                    if product.stock <= product.min_stock_alert:
                        try:
                            from notifications.utils import notify_low_stock
                            notify_low_stock(product)
                        except:
                            pass  # Don't fail order if notification fails
            
            # ============================================================
            # STEP 9: Cart Is Fully Cleared
            # ============================================================
            # Clear cart - delete all cart items and the cart
            cart_items.delete()
            try:
                cart.delete()
            except:
                pass
            
            # ============================================================
            # STEP 10: Order is Finalized
            # ============================================================
            # Mark order as officially placed
            order.is_ordered = True
            order.status = 'New'
            order.save()
            
            # Create order tracking entry
            from orders.models import OrderTracking
            OrderTracking.objects.create(
                order=order,
                status='New',
                description='Order placed successfully'
            )
            
            # ============================================================
            # STEP 12: Seller/Admin Gets Notified
            # ============================================================
            # Send notifications to admin and customer
            from notifications.utils import notify_new_order
            notify_new_order(order)
            
            # Send invoice email
            try:
                from orders.utils import send_invoice_email
                send_invoice_email(order)
            except:
                pass  # Don't fail order if email fails
            
            # ============================================================
            # STEP 11: Confirmation Page Shows Order Number
            # ============================================================
            messages.success(request, f'Order placed successfully! Your order number is {order_number}')
            return redirect('orders:order_success', order_number=order_number)
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        # Pre-fill form with user data if available
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'phone': request.user.phone_number if hasattr(request.user, 'phone_number') else '',
                'address_line_1': request.user.address_line_1,
                'address_line_2': request.user.address_line_2,
                'city': request.user.city,
                'state': request.user.state,
                'country': request.user.country,
                'pincode': request.user.pincode,
            }
        form = OrderForm(initial=initial_data)
    
    # Get applied coupon if any
    applied_coupon = None
    discount = 0
    if 'applied_coupon' in request.session:
        try:
            from coupons.models import Coupon
            coupon_id = request.session.get('applied_coupon')
            applied_coupon = Coupon.objects.get(id=coupon_id)
            discount = request.session.get('coupon_discount', 0)
        except:
            pass
    
    # Check if Razorpay is enabled
    from orders.payment_utils import is_razorpay_enabled
    razorpay_enabled = is_razorpay_enabled()
    
    user_has_saved_address = False
    if request.user.is_authenticated:
        user_has_saved_address = all([
            request.user.address_line_1,
            request.user.city,
            request.user.state,
            request.user.country,
            request.user.pincode,
        ])

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'discount': discount,
        'grand_total': grand_total,
        'form': form,
        'applied_coupon': applied_coupon,
        'razorpay_enabled': razorpay_enabled,  # Pass to template
        'user_has_saved_address': user_has_saved_address,
    }
    return render(request, 'store/checkout.html', context)


@login_required(login_url='accounts:login')
def order_success(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
        order_products = OrderProduct.objects.filter(order=order)
        
        context = {
            'order': order,
            'order_products': order_products,
        }
        return render(request, 'store/order_success.html', context)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('store')