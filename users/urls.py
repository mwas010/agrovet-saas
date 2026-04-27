"""
Users app URLs.
"""

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('manage-passwords/', views.manage_passwords, name='manage_passwords'),
    path('change-password/<int:user_id>/', views.change_password, name='change_password'),
]
