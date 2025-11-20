from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from cart.models import Cart, CartItem
from notifications.utils import send_email_notification, create_notification
from django.conf import settings


class Command(BaseCommand):
    help = 'Check and mark abandoned carts, send reminders'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Hours after which cart is considered abandoned (default: 24)',
        )
        parser.add_argument(
            '--send-reminders',
            action='store_true',
            help='Send email reminders to users with abandoned carts',
        )

    def handle(self, *args, **options):
        hours = options['hours']
        send_reminders = options['send_reminders']
        
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        # Find carts that haven't been updated in the specified hours
        abandoned_carts = Cart.objects.filter(
            date_added__lt=cutoff_time.date(),
            is_abandoned=False
        ).exclude(user__isnull=True)  # Only logged-in users
        
        count = 0
        reminder_count = 0
        
        for cart in abandoned_carts:
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            
            if cart_items.exists():
                # Mark as abandoned
                cart.is_abandoned = True
                cart.abandoned_at = timezone.now()
                cart.save()
                count += 1
                
                # Send reminder if requested and user has email
                if send_reminders and cart.user and cart.user.email:
                    if not cart.reminder_sent or cart.reminder_count < 3:
                        self.send_abandoned_cart_reminder(cart, cart_items)
                        cart.reminder_count += 1
                        cart.reminder_sent = True
                        cart.save()
                        reminder_count += 1
                        
                        # Notify admin
                        create_notification(
                            notification_type='abandoned_cart',
                            title=f'Abandoned Cart - {cart.user.email}',
                            message=f'User {cart.user.email} has an abandoned cart with {cart_items.count()} items',
                            is_admin_notification=True
                        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully marked {count} carts as abandoned. '
                f'Sent {reminder_count} reminders.'
            )
        )

    def send_abandoned_cart_reminder(self, cart, cart_items):
        """Send email reminder for abandoned cart"""
        if not cart.user or not cart.user.email:
            return
        
        # Calculate cart total
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
        
        Complete your purchase now: {settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/cart/
        
        This offer won't last forever!
        
        Best regards,
        Aromas by HarNoor Team
        """
        
        send_email_notification(
            cart.user.email,
            subject,
            message,
            'abandoned_cart'
        )

