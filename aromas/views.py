from django.shortcuts import render
from store.models import Product

def home(request):
    products = Product.objects.all().filter(is_available=True)
    print(products) #debugging purpose for products
    print("products fetched successfully") #debugging purpose for products
    context = {
        'products': products,
    }
    return render(request,'home.html',context)