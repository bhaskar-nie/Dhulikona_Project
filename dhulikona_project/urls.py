"""
URL configuration for dhulikona_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from water_management.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name="homepage"),
    path('portal/login', adminlogin, name="adminlogin"),
    path('admin-panel', adminpage),
    path('logout/', logoutuser, name="logoutuser"),
    path('panchayatheadpage/<str:panchayat_name>/', panchayatheadpage, name='panchayatheadpage'),
    path('toggle_consumer_status/<int:consumer_id>/', toggle_consumer_status, name='toggle_consumer_status'),
    path('update-water-fee-rate/', update_water_fee_rate, name='update_water_fee_rate'),
    path('panchayat-head-mgmt/', panchayatheadmgmt, name="panchayatheadmgmt"),
    path('toggle-panchayat-head/<int:head_id>/', toggle_panchayat_head_status, name='toggle_panchayat_head_status'),
    path('update-panchayat-head/<int:panchayat_id>/', update_panchayat_head, name='update_panchayat_head'),
    path('gram-panchayat-management/', gram_panchayat_management, name='gram_panchayat_management'),
    path('add-panchayat/', add_panchayat, name='add_panchayat'),
    path('assign-panchayat-head/<int:panchayat_id>/', assign_panchayat_head, name='assign_panchayat_head'),
    path('view-consumers/', view_consumers, name='viewconsumers'),
]

# Part A for static files
urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#part B
# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files during development
urlpatterns += staticfiles_urlpatterns()