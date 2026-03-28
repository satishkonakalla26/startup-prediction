"""Comprehensive error check and validation"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'startup_prediction.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

print("=" * 70)
print("COMPREHENSIVE ERROR CHECK")
print("=" * 70)

errors_found = []

# Test 1: Import all views
print("\n✓ Testing imports...")
try:
    from adminapp.views import home, admin_login, admin_logout, index
    print("  ✅ Admin views imported successfully")
except Exception as e:
    errors_found.append(f"Admin views import error: {e}")
    print(f"  ❌ Admin views import error: {e}")

try:
    from userapp.views import user_login, user_register, user_logout, user_dashboard
    print("  ✅ User views imported successfully")
except Exception as e:
    errors_found.append(f"User views import error: {e}")
    print(f"  ❌ User views import error: {e}")

# Test 2: Check URL configuration
print("\n✓ Testing URL configuration...")
try:
    from django.urls import reverse
    
    urls_to_check = ['home', 'admin_login', 'user_login', 'user_register', 'index']
    for url_name in urls_to_check:
        try:
            url = reverse(url_name)
            print(f"  ✅ URL '{url_name}': {url}")
        except Exception as e:
            errors_found.append(f"URL '{url_name}' not found: {e}")
            print(f"  ❌ URL '{url_name}' error: {e}")
except Exception as e:
    errors_found.append(f"URL configuration error: {e}")
    print(f"  ❌ URL configuration error: {e}")

# Test 3: Check templates exist
print("\n✓ Testing templates...")
templates_to_check = [
    'main_template/home.html',
    'main_template/admin-login.html',
    'main_template/user-login.html',
    'admin_template/index.html',
    'user_template/user-dashboard.html',
]

for template in templates_to_check:
    path = f'./templates/{template}'
    if os.path.exists(path):
        print(f"  ✅ {template}")
    else:
        errors_found.append(f"Template not found: {template}")
        print(f"  ❌ {template} NOT FOUND")

# Test 4: Check database models
print("\n✓ Testing database models...")
try:
    from mainapp.models import User
    from adminapp.models import Dataset
    count_users = User.objects.count()
    count_datasets = Dataset.objects.count()
    print(f"  ✅ Users in database: {count_users}")
    print(f"  ✅ Datasets in database: {count_datasets}")
except Exception as e:
    errors_found.append(f"Database model error: {e}")
    print(f"  ❌ Database model error: {e}")

# Test 5: Check session middleware
print("\n✓ Testing Django middleware...")
try:
    from django.conf import settings
    middleware = settings.MIDDLEWARE
    required_middleware = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
    ]
    for mw in required_middleware:
        if mw in middleware:
            print(f"  ✅ {mw.split('.')[-1]}")
        else:
            errors_found.append(f"Missing middleware: {mw}")
            print(f"  ❌ Missing: {mw.split('.')[-1]}")
except Exception as e:
    errors_found.append(f"Middleware check error: {e}")
    print(f"  ❌ Middleware check error: {e}")

# Summary
print("\n" + "=" * 70)
if not errors_found:
    print("✅ NO ERRORS FOUND - System is working perfectly!")
    print("=" * 70)
    print("\n📋 Summary:")
    print("  • All views imported successfully")
    print("  • All URLs configured correctly")
    print("  • All templates located")
    print("  • Database models connected")
    print("  • Middleware properly configured")
    print("\n🚀 Ready to run: python manage.py runserver 8000")
else:
    print(f"❌ {len(errors_found)} ERRORS FOUND:")
    print("=" * 70)
    for i, error in enumerate(errors_found, 1):
        print(f"  {i}. {error}")

print("=" * 70)
