from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from adminapp import views as admin_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',       admin_views.home,  name='home'),
    path('',       include('adminapp.urls')),
    path('user/',  include('userapp.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
