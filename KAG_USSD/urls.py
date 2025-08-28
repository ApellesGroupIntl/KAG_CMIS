"""
URL configuration for KAG_USSD project.

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
from django.urls import path, include
from USSD_CORE import views
from django.shortcuts import redirect

def root_redirect(request):
    return redirect('accounts:login')

urlpatterns = [
    path('', root_redirect),
    path('admin/', admin.site.urls),
    # path("ussd/", include("USSD_CORE.urls", namespace="USSD_CORE")),
    path('', include('USSD_CORE.urls')),
    path("mpesa/", include("Mpesa.urls")),
    path('api/mpesa/', include('Mpesa.urls')),
    path('dashboard/', views.dashboard, name='dashboard'),  # Define it here
    path('local-church/', include('Local_Church.urls')),  # ← Add this line
    path("USSD_CORE/", include("USSD_CORE.urls")),  # ✅ mounts all app urls
    # path("accounts/", include("accounts.urls")),
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),

    #path('users/', include('Users.urls')),
]
