from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
from django.db.models import Sum

from .forms import RegistrationForm, UserProfileForm, ChangePasswordForm, ForgotPasswordForm, ResetPasswordForm
from .models import Account, LoginAttempt
from orders.models import Order, OrderProduct
from .utils import send_verification_email, verify_token, send_password_reset_email, verify_password_reset_token


def _get_client_ip(request):
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']

            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while Account.objects.filter(username=username).exists():
                username = f'{base_username}{counter}'
                counter += 1

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )
            user.phone_number = phone_number
            user.is_active = False  # User is inactive until email is verified
            user.save()

            # Send verification email
            try:
                send_verification_email(request, user)
                messages.success(request, 'Registration successful! We have sent a verification email to your email address. Please check your email and click the verification link to activate your account.')
            except Exception as e:
                # If email fails, still create user but show error message
                messages.warning(request, f'Registration successful! However, we could not send the verification email. Error: {str(e)}. Please contact support.')

            # Ensure user is NOT logged in after registration
            auth.logout(request)

            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()

    context = {'form': form}
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        email = email.lower().strip() if email else ''

        user = auth.authenticate(request, email=email, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, 'Your account is not activated. Please check your email and verify your account by clicking the verification link we sent you.')
                next_url = request.POST.get('next', request.GET.get('next', ''))
                if next_url:
                    return redirect(f"{reverse('accounts:login')}?next={next_url}")
                return redirect('accounts:login')
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            
            # Get next URL from POST (form) or GET (query string)
            next_url = request.POST.get('next', request.GET.get('next', ''))
            
            # Validate next URL to prevent open redirects
            if next_url:
                # Check if it's a relative URL (starts with /)
                if next_url.startswith('/'):
                    return redirect(next_url)
                # If it's a URL name, try to resolve it
                try:
                    return redirect(next_url)
                except:
                    pass
            
            # Default redirect to dashboard
            return redirect('accounts:dashboard')
        else:
            if Account.objects.filter(email__iexact=email).exists():
                messages.error(request, 'Incorrect password. Please try again.')
            else:
                messages.error(request, 'No account found with that email.')
            next_url = request.POST.get('next', request.GET.get('next', ''))
            if next_url:
                return redirect(f"{reverse('accounts:login')}?next={next_url}")
            return redirect('accounts:login')

    # Preserve next parameter in GET request
    next_url = request.GET.get('next', '')
    context = {'next_url': next_url}
    return render(request, 'accounts/login.html', context)


def activate(request, uidb64, token):
    """Activate user account via email verification"""
    user = verify_token(uidb64, token)
    
    if user is not None:
        # Check if already activated
        if user.is_active:
            context = {
                'success': True,
                'message': 'Your email has already been verified. You can log in to your account.',
                'already_verified': True
            }
            return render(request, 'accounts/email_verification.html', context)
        
        user.is_active = True
        user.save()
        context = {
            'success': True,
            'message': 'Congratulations! Your email has been successfully verified. You can now log in to your account.',
            'user': user
        }
        return render(request, 'accounts/email_verification.html', context)
    else:
        context = {
            'success': False,
            'message': 'Invalid activation link. The link may have expired or already been used. Please register again or contact support if you continue to experience issues.'
        }
        return render(request, 'accounts/email_verification.html', context)


@login_required(login_url='accounts:login')
def dashboard(request):
    """User dashboard showing profile information"""
    user = request.user
    orders = Order.objects.filter(user=user, is_ordered=True).order_by('-created_at')
    recent_orders = orders[:5]
    total_orders = orders.count()
    completed_orders = orders.filter(status__in=['Delivered', 'Completed']).count()
    pending_orders = orders.exclude(status__in=['Delivered', 'Completed', 'Cancelled']).count()
    cancelled_orders = orders.filter(status='Cancelled').count()
    total_spent = orders.aggregate(total=Sum('final_total'))['total'] or 0
    
    context = {
        'user': user,
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'cancelled_orders': cancelled_orders,
        'total_spent': total_spent,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='accounts:login')
def edit_profile(request):
    """Edit user profile"""
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='accounts:login')
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password']
            
            # Check if current password is correct
            if not user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
                return redirect('accounts:change_password')
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            # Update session to prevent logout
            update_session_auth_hash(request, user)
            
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ChangePasswordForm()
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/change_password.html', context)


def forgot_password(request):
    """Handle forgot password form submission"""
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = Account.objects.get(email__iexact=email)
                # Send password reset email
                try:
                    send_password_reset_email(request, user)
                    messages.success(request, 'Password reset link has been sent to your email address. Please check your email and follow the instructions to reset your password.')
                    return redirect('accounts:login')
                except Exception as e:
                    messages.error(request, f'Failed to send password reset email. Error: {str(e)}. Please try again later or contact support.')
            except Account.DoesNotExist:
                # Don't reveal if email exists for security reasons
                messages.success(request, 'If an account with that email exists, a password reset link has been sent to your email address.')
                return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ForgotPasswordForm()
    
    context = {'form': form}
    return render(request, 'accounts/forgot_password.html', context)


def reset_password(request, uidb64, token):
    """Handle password reset via token"""
    user = verify_password_reset_token(uidb64, token)
    
    if user is None:
        messages.error(request, 'Invalid or expired password reset link. Please request a new one.')
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Your password has been reset successfully! You can now log in with your new password.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ResetPasswordForm()
    
    context = {
        'form': form,
        'uidb64': uidb64,
        'token': token,
    }
    return render(request, 'accounts/reset_password.html', context)


@login_required(login_url='accounts:login')
def account_statistics(request):
    """Display account statistics"""
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'accounts/account_statistics.html', context)


@login_required(login_url='accounts:login')
def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, 'You have been logged out.')
        return redirect('accounts:login')
    messages.info(request, 'Please confirm logout.')
    return redirect('store')


def honeypot_admin_login(request):
    """Fake admin login page that records attempts."""
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = Account.objects.filter(email__iexact=username).first()
        LoginAttempt.objects.create(
            user=user,
            email=username,
            ip_address=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
            success=False,
        )
        error_message = 'Invalid username or password.'
    return render(request, 'admin_honeypot/login.html', {
        'error_message': error_message,
    })
