"""
Reports app URLs.
"""

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.sales_report, name='sales_report'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('export/excel/', views.export_excel, name='export_excel'),
]
