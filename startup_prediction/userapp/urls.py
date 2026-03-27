from django.urls import path
from userapp import views

urlpatterns = [
    path('login/',           views.user_login,     name='user_login'),
    path('register/',        views.user_register,  name='user_register'),
    path('logout/',          views.user_logout,    name='user_logout'),
    path('dashboard/',       views.user_dashboard, name='dashboard'),
    path('prediction/',      views.prediction,     name='prediction'),
    path('profile/',         views.user_profile,   name='user_profile'),
    path('predict-startup/', views.predict_startup, name='predict_startup'),
    path('resources/',       views.resources,      name='resources'),
    path('my-predictions/',  views.my_predictions, name='my_predictions'),
]
