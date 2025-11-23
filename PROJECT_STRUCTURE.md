# Project File Structure

## Root Directory
```
Aromas by harnoor/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── gunicorn_config.py
├── nginx.conf
├── nginx_config.conf
├── env.example
├── check_code.py
├── deploy_setup.py
├── run_network.bat
├── run_server_network.py
├── send_notification.py
```

## Documentation Files
```
├── README.md
├── ALL_FEATURES_EXPLAINED.md
├── COMPLETE_FEATURES_GUIDE.md
├── DEPLOYMENT_GUIDE.md
├── DEVELOPMENT_GUIDE.md
├── DOCKER_DEPLOYMENT.md
├── FEATURES_CHECKLIST.md
├── PROJECT_FEATURES.md
├── QUICK_DEPLOY.md
├── QUICK_START.md
├── RAZORPAY_SETUP.md
├── SELLER_LOGIN_GUIDE.md
└── STOCK_REDUCTION_VERIFICATION.md
```

## Django Apps

### accounts/
```
accounts/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── signals.py
├── tests.py
├── urls.py
├── utils.py
├── views.py
└── migrations/
    ├── __init__.py
    ├── 0001_initial.py
    ├── 0002_alter_account_is_active.py
    ├── 0003_alter_account_is_active.py
    ├── 0004_alter_account_is_active.py
    ├── 0005_account_profile_image.py
    ├── 0006_account_address_fields.py
    └── 0007_loginattempt.py
```

### aromas/ (Main Project Settings)
```
aromas/
├── __init__.py
├── settings.py
├── settings_production.py
├── urls.py
├── views.py
├── wsgi.py
├── asgi.py
└── static/
    ├── css/
    │   ├── *.css (3 files)
    │   └── *.map (2 files)
    ├── fonts/
    │   ├── *.ttf (8 files)
    │   ├── *.css (4 files)
    │   ├── *.eot (3 files)
    │   └── other font files
    ├── images/
    │   ├── *.jpg (21 files)
    │   ├── *.png (18 files)
    │   ├── *.svg (2 files)
    │   └── other image files
    └── js/
        └── *.js (3 files)
```

### cart/
```
cart/
├── __init__.py
├── admin.py
├── admin_views.py
├── apps.py
├── context_processors.py
├── forms.py
├── models.py
├── tests.py
├── urls.py
├── views.py
├── migrations/
│   ├── __init__.py
│   ├── 0001_initial.py
│   ├── 0002_cartitem_variations.py
│   ├── 0003_order_payment_orderproduct_order_payment.py
│   └── 0004_remove_orderproduct_order_and_more.py
└── management/
    └── commands/
        └── *.py (2 files)
```

### category/
```
category/
├── __init__.py
├── admin.py
├── apps.py
├── context_processors.py
├── models.py
├── tests.py
├── views.py
└── migrations/
    ├── __init__.py
    ├── 0001_initial.py
    └── 0002_alter_category_slug.py
```

### coupons/
```
coupons/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── tests.py
├── urls.py
├── views.py
└── migrations/
    └── __init__.py
```

### loyalty/
```
loyalty/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── tests.py
├── urls.py
├── views.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### notifications/
```
notifications/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── tests.py
├── utils.py
├── views.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### orders/
```
orders/
├── __init__.py
├── admin.py
├── admin_views.py
├── apps.py
├── forms.py
├── models.py
├── payment_utils.py
├── tests.py
├── urls.py
├── utils.py
├── views.py
└── migrations/
    └── *.py (4 files)
```

### reviews/
```
reviews/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── tests.py
├── urls.py
├── views.py
└── migrations/
    └── *.py (3 files)
```

### seller/
```
seller/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── tests.py
├── urls.py
├── views.py
└── migrations/
    └── __init__.py
```

### store/
```
store/
├── __init__.py
├── admin.py
├── admin_views.py
├── apps.py
├── models.py
├── tests.py
├── urls.py
├── utils.py
├── views.py
└── migrations/
    └── *.py (4 files)
```

### wishlist/
```
wishlist/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── tests.py
├── urls.py
├── views.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

## Templates/
```
templates/
├── base.html
├── home.html
├── product_detail.html
├── accounts/
│   └── *.html (11 files)
├── admin_honeypot/
│   └── login.html
├── includes/
│   └── *.html (3 files)
├── orders/
│   └── *.html (4 files)
├── policies/
│   └── *.html (6 files)
├── seller/
│   └── *.html (2 files)
└── store/
    └── *.html (4 files)
```

## Static Files (Collected)
```
static/
├── admin/
│   ├── css/
│   ├── img/
│   └── js/
├── css/
├── fonts/
├── images/
└── js/
```

## Media Files
```
media/
└── photos/
    ├── categorie5/
    ├── products/
    └── profile_images/
```

## Virtual Environment
```
venv/
├── Include/
├── Lib/
├── Scripts/
└── pyvenv.cfg
```

## Project Summary

### Django Apps (11 total):
1. **accounts** - User authentication and account management
2. **aromas** - Main project configuration
3. **cart** - Shopping cart functionality
4. **category** - Product categories
5. **coupons** - Coupon/discount system
6. **loyalty** - Loyalty program
7. **notifications** - Notification system
8. **orders** - Order management and payment processing
9. **reviews** - Product reviews
10. **seller** - Seller management
11. **store** - Store/product management
12. **wishlist** - Wishlist functionality

### Key Features:
- E-commerce platform with shopping cart
- User authentication and profiles
- Product management with categories
- Order processing with payment integration (Razorpay)
- Reviews and ratings
- Wishlist functionality
- Coupon system
- Loyalty program
- Seller management
- Notification system
- Docker deployment support
- Nginx configuration
- Production settings

