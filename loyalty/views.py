from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import LoyaltyPoints, PointsTransaction, ReferralCode, Referral
from accounts.models import Account
import secrets
import string


@login_required(login_url='accounts:login')
def loyalty_dashboard(request):
    """User loyalty points dashboard"""
    loyalty_points, created = LoyaltyPoints.objects.get_or_create(user=request.user)
    transactions = PointsTransaction.objects.filter(user=request.user).order_by('-created_at')[:20]
    
    # Get referral code
    referral_code, created = ReferralCode.objects.get_or_create(user=request.user)
    if created:
        # Generate unique code
        code = f"REF{request.user.id}{''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))}"
        referral_code.code = code
        referral_code.save()
    
    # Get referrals
    referrals = Referral.objects.filter(referrer=request.user)
    
    context = {
        'loyalty_points': loyalty_points,
        'transactions': transactions,
        'referral_code': referral_code,
        'referrals': referrals,
    }
    return render(request, 'loyalty/dashboard.html', context)


@login_required(login_url='accounts:login')
def generate_referral_code(request):
    """Generate or regenerate referral code"""
    referral_code, created = ReferralCode.objects.get_or_create(user=request.user)
    
    if not created and referral_code.code:
        messages.info(request, f'Your referral code is: {referral_code.code}')
        return redirect('loyalty:dashboard')
    
    # Generate unique code
    code = f"REF{request.user.id}{''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))}"
    referral_code.code = code
    referral_code.save()
    
    messages.success(request, f'Your referral code is: {code}')
    return redirect('loyalty:dashboard')
