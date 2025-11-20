from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponse
import csv
from .models import Product, ProductImage
from category.models import Category


@staff_member_required
def bulk_upload_products(request):
    """Bulk upload products from CSV"""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('admin:store_product_changelist')
        
        try:
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(decoded_file.splitlines())
            
            success_count = 0
            error_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_data, start=2):
                try:
                    # Get or create category
                    category_name = row.get('category', '').strip()
                    if not category_name:
                        errors.append(f"Row {row_num}: Category is required")
                        error_count += 1
                        continue
                    
                    category, _ = Category.objects.get_or_create(
                        Category_name=category_name,
                        defaults={'slug': category_name.lower().replace(' ', '-')}
                    )
                    
                    # Create product
                    product_name = row.get('product_name', '').strip()
                    if not product_name:
                        errors.append(f"Row {row_num}: Product name is required")
                        error_count += 1
                        continue
                    
                    # Check if product exists
                    if Product.objects.filter(product_name=product_name).exists():
                        errors.append(f"Row {row_num}: Product '{product_name}' already exists")
                        error_count += 1
                        continue
                    
                    product = Product.objects.create(
                        product_name=product_name,
                        slug=row.get('slug', product_name.lower().replace(' ', '-')),
                        description=row.get('description', ''),
                        price=int(row.get('price', 0)),
                        stock=int(row.get('stock', 0)),
                        is_available=row.get('is_available', 'True').lower() == 'true',
                        category=category,
                        sale_price=int(row.get('sale_price', 0)) if row.get('sale_price') else None,
                        is_featured=row.get('is_featured', 'False').lower() == 'true',
                    )
                    
                    success_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    error_count += 1
            
            if success_count > 0:
                messages.success(request, f'Successfully imported {success_count} products.')
            if error_count > 0:
                messages.warning(request, f'{error_count} products failed to import. Check errors below.')
                for error in errors[:10]:  # Show first 10 errors
                    messages.error(request, error)
            
            return redirect('admin:store_product_changelist')
            
        except Exception as e:
            messages.error(request, f'Error processing CSV file: {str(e)}')
            return redirect('admin:store_product_changelist')
    
    return render(request, 'admin/bulk_upload.html')

