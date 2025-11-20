from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Wishlist, WishlistItem
from store.models import Product


@login_required(login_url='accounts:login')
def wishlist(request):
    """View user's wishlist"""
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_items = wishlist.items.all()
    
    context = {
        'wishlist': wishlist,
        'wishlist_items': wishlist_items,
    }
    return render(request, 'wishlist/wishlist.html', context)


@login_required(login_url='accounts:login')
def add_to_wishlist(request, product_id):
    """Add product to wishlist"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        
        # Check if already in wishlist
        if WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Product already in wishlist'})
            messages.info(request, 'Product is already in your wishlist.')
        else:
            WishlistItem.objects.create(wishlist=wishlist, product=product)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Added to wishlist'})
            messages.success(request, 'Product added to wishlist.')
    
    return redirect('product_detail', product_slug=product.slug)


@login_required(login_url='accounts:login')
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        wishlist = get_object_or_404(Wishlist, user=request.user)
        wishlist_item = get_object_or_404(WishlistItem, wishlist=wishlist, product=product)
        wishlist_item.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Removed from wishlist'})
        messages.success(request, 'Product removed from wishlist.')
    
    return redirect('wishlist:wishlist')
