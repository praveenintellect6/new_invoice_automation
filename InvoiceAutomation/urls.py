"""
URL configuration for InvoiceAutomation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mainapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home_view'),
    path('add_supplier/',views.add_supplier,name="add_supplier"),
    path('get_suppliers/', views.get_suppliers, name="get_suppliers"),
    path('delete_supplier/', views.delete_supplier, name="delete_supplier"),
    path('fetch_columns/', views.fetch_columns, name="fetch_columns"),
    path('add_update_columns/', views.add_update_columns, name="add_update_columns"),
    path('save_edited_columns/', views.save_edited_columns, name="save_edited_columns"),
    path('save_edited_case/',views.save_edited_case,name="save_edited_case"),
    path("fetch_case/",views.fetch_case,name="fetch_case"),
    path('submit_excel_files/',views.submit_excel_files,name='submit_excel_files'),
    path('submit_edit_excel_files/', views.submit_edit_excel_files, name='submit_edit_excel_files'),
    path('submit_pdf_files/', views.submit_pdf_files, name='submit_pdf_files'),
    path('monthReportGenerate/', views.monthReportGenerate, name='monthReportGenerate'),
]
