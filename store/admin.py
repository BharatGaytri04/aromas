from django.contrib import admin
from .models import Product
from django.db import models

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
   
admin.site.register(Product, ProductAdmin)