from django.urls import path
from adminapp import views

urlpatterns = [
    # Auth
    path('admin-login/',  views.admin_login,  name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),

    # API
    path('api/stats/', views.get_stats, name='get_stats'),

    # Dashboard
    path('index/', views.index, name='index'),

    # User Management
    path('pending-users/',       views.pending_users, name='pending_users'),
    path('all-users/',           views.all_users,     name='all_users'),
    path('accept/<int:id>/',     views.accept,         name='accept'),
    path('reject/<int:id>/',     views.reject,         name='reject'),
    path('change-status/<int:id>/', views.change_status, name='change_status'),
    path('remove/<int:id>/',     views.remove,         name='remove'),

    # Dataset
    path('upload-dataset/', views.upload_dataset, name='upload_dataset'),
    path('view-dataset/',   views.view_dataset,   name='view_dataset'),

    # Algorithms
    path('algorithm1/', views.gradient_boosting_classifier, name='algorithm1'),
    path('algorithm2/', views.ada_boost_classifier,         name='algorithm2'),
    path('algorithm3/', views.random_forest_classifier,     name='algorithm3'),
    path('nb-alg/',     views.NB_alg,                       name='NB_alg'),
    path('xgb-alg/',    views.XGB_alg,                      name='XGB_alg'),

    # Run Algorithm Buttons
    path('gbc-run/<int:id>/', views.gbc_runalgo, name='gbc_runalgo'),
    path('ada-run/<int:id>/', views.ada_runalgo, name='ada_runalgo'),
    path('rfc-run/<int:id>/', views.rfc_runalgo, name='rfc_runalgo'),
    path('nb-run/',           views.NB_btn,       name='NB_btn'),
    path('xgb-run/',          views.XGB_btn,      name='XGB_btn'),

    # Graph Analysis
    path('graph-analysis/', views.graph_analasis, name='graph_analasis'),
]
