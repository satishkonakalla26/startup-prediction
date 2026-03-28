"""Verify all templates render without errors"""
import os
import django
from django.template.loader import render_to_string
from django.test import RequestFactory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'startup_prediction.settings')
django.setup()

print("=" * 70)
print("TEMPLATE RENDERING CHECK")
print("=" * 70)

templates_to_test = {
    'main_template/home.html': ['Admin Login', 'User Login', 'Register'],
    'main_template/admin-login.html': ['Admin Login', 'Login', 'Remember me'],
    'main_template/user-login.html': ['User Login', 'Email Address', 'Register'],
    'main_template/user-register.html': ['Register', 'Email', 'Password'],
}

all_passed = True

for template_name, keywords in templates_to_test.items():
    try:
        req = RequestFactory().get('/')
        req.session = {}
        template_str = render_to_string(template_name, {}, request=req)
        
        print(f"\n✅ {template_name}")
        print(f"   Size: {len(template_str)} characters")
        
        missing_keywords = []
        for keyword in keywords:
            if keyword not in template_str:
                missing_keywords.append(keyword)
        
        if missing_keywords:
            print(f"   ⚠️  Missing keywords: {missing_keywords}")
        else:
            print(f"   ✅ All keywords found: {', '.join(keywords)}")
    
    except Exception as e:
        all_passed = False
        print(f"\n❌ {template_name}")
        print(f"   Error: {e}")

print("\n" + "=" * 70)
if all_passed:
    print("✅ ALL TEMPLATES RENDER SUCCESSFULLY!")
else:
    print("❌ SOME TEMPLATES HAVE ERRORS - CHECK ABOVE")
print("=" * 70)
