from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count
from store.models import Product
from orders.models import OrderProduct
from .models import Review
from .forms import ReviewForm


@login_required(login_url='accounts:login')
def submit_review(request, product_slug):
    """
    Submit a review for a product.
    Only users who have purchased the product can review it.
    """
    product = get_object_or_404(Product, slug=product_slug, is_available=True)
    
    # Check if user has purchased this product
    has_purchased = OrderProduct.objects.filter(
        user=request.user,
        product=product,
        ordered=True
    ).exists()
    
    if not has_purchased:
        messages.warning(
            request, 
            'You can only review products you have purchased. Please purchase this product first.'
        )
        return redirect('product_detail', product_slug=product_slug)
    
    # Check if user already reviewed this product
    existing_review = Review.objects.filter(
        product=product,
        user=request.user
    ).first()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_approved = True  # Auto-approve for now (can be changed to False for moderation)
            review.save()
            
            if existing_review:
                messages.success(request, 'Your review has been updated successfully!')
            else:
                messages.success(request, 'Thank you for your review!')
            
            return redirect('product_detail', product_slug=product_slug)
        else:
            messages.error(request, 'Please correct the errors in your review.')
    else:
        form = ReviewForm(instance=existing_review)
    
    context = {
        'product': product,
        'form': form,
        'existing_review': existing_review,
    }
    return render(request, 'reviews/submit_review.html', context)


@login_required(login_url='accounts:login')
def submit_review_ajax(request, product_id):
    """
    Submit review via AJAX (for better UX).
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})
    
    product = get_object_or_404(Product, id=product_id, is_available=True)
    
    # Check if user has purchased this product
    has_purchased = OrderProduct.objects.filter(
        user=request.user,
        product=product,
        ordered=True
    ).exists()
    
    if not has_purchased:
        return JsonResponse({
            'success': False,
            'message': 'You can only review products you have purchased.'
        })
    
    # Get or create review
    review, created = Review.objects.get_or_create(
        product=product,
        user=request.user,
        defaults={'rating': 0, 'review_text': ''}
    )
    
    # Update review
    rating = request.POST.get('rating')
    review_text = request.POST.get('review_text', '').strip()
    
    if not rating:
        return JsonResponse({'success': False, 'message': 'Please provide a rating.'})
    
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return JsonResponse({'success': False, 'message': 'Rating must be between 1 and 5.'})
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Invalid rating value.'})
    
    review.rating = rating
    review.review_text = review_text[:1000]  # Limit to 1000 characters
    review.is_approved = True  # Auto-approve
    review.save()
    
    # Calculate updated average rating
    reviews = Review.objects.filter(product=product, is_approved=True)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    review_count = reviews.count()
    
    return JsonResponse({
        'success': True,
        'message': 'Review submitted successfully!' if created else 'Review updated successfully!',
        'avg_rating': round(avg_rating, 1),
        'review_count': review_count,
        'rating': rating,
        'review_text': review.review_text,
    })


def get_product_reviews(request, product_slug):
    """
    Get reviews for a product (for AJAX loading).
    """
    product = get_object_or_404(Product, slug=product_slug, is_available=True)
    
    # Get approved reviews
    reviews = Review.objects.filter(product=product, is_approved=True).order_by('-created_at')
    
    # Pagination
    from django.core.paginator import Paginator
    page = request.GET.get('page', 1)
    paginator = Paginator(reviews, 5)  # 5 reviews per page
    reviews_page = paginator.get_page(page)
    
    reviews_data = []
    for review in reviews_page:
        reviews_data.append({
            'id': review.id,
            'user_name': review.user.get_display_name(),  # Privacy-friendly: shows name, never email
            'rating': review.rating,
            'review_text': review.review_text,
            'created_at': review.created_at.strftime('%B %d, %Y'),
            'updated_at': review.updated_at.strftime('%B %d, %Y') if review.updated_at != review.created_at else None,
        })
    
    return JsonResponse({
        'success': True,
        'reviews': reviews_data,
        'has_next': reviews_page.has_next(),
        'has_previous': reviews_page.has_previous(),
        'current_page': reviews_page.number,
        'total_pages': paginator.num_pages,
    })


@login_required(login_url='accounts:login')
def delete_review(request, review_id):
    """
    Delete user's own review.
    """
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_slug = review.product.slug
    review.delete()
    
    messages.success(request, 'Your review has been deleted.')
    return redirect('product_detail', product_slug=product_slug)
