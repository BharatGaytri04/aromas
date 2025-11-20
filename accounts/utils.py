from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse


def send_verification_email(request, user):
    """Send email verification link to user"""
    current_site = request.get_host()
    mail_subject = 'Welcome to Aromas by HarNoor - Verify Your Email Address'
    
    # Generate verification token
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Create verification link
    verification_path = reverse('accounts:activate', args=[uid, token])
    verification_link = request.build_absolute_uri(verification_path)
    
    # Render email template
    message = render_to_string('accounts/account_verification_email.html', {
        'user': user,
        'verification_link': verification_link,
        'current_site': current_site,
    })
    
    # Send email
    to_email = user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.content_subtype = 'html'  # Set email content as HTML
    email.send()


def verify_token(uidb64, token):
    """Verify the token and activate the user account"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        from .models import Account
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        return user
    return None


def send_password_reset_email(request, user):
    """Send password reset link to user"""
    current_site = request.get_host()
    mail_subject = 'Reset Your Password - Aromas by HarNoor'
    
    # Generate password reset token
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Create password reset link
    reset_path = reverse('accounts:reset_password', args=[uid, token])
    reset_link = request.build_absolute_uri(reset_path)
    
    # Render email template
    message = render_to_string('accounts/password_reset_email.html', {
        'user': user,
        'reset_link': reset_link,
        'current_site': current_site,
    })
    
    # Send email
    to_email = user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.content_subtype = 'html'  # Set email content as HTML
    email.send()


def verify_password_reset_token(uidb64, token):
    """Verify the password reset token"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        from .models import Account
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        return user
    return None

