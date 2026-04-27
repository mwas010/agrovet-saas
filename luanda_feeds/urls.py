"""
Luanda Feeds Centre - Agrovet Automation Software
URL Configuration.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('inventory/', include('inventory.urls')),
    path('sales/', include('sales.urls')),
    path('reports/', include('reports.urls')),
    path('', lambda request: HttpResponseRedirect('/users/login/')),
]
