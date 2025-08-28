from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
app_name = "USSD_CORE"   # ✅ Add this line


urlpatterns = [
    path("home/", views.ussd_home, name="ussd-home"),
    path("ussd/", views.ussd_callback, name="ussd_callback"),
    path("ussd_section/", views.ussd_callback_section, name="ussd_callback_section"),
    path('ussd_reg/', views.ussd_registration_view, name='ussd_registration'),
    path("transactions/", views.transaction_list, name="transaction_list"),
    path("transactions/<int:pk>/", views.transaction_detail, name="transaction_detail"),
    path("dashboard/", views.dashboard, name="dashboard"),  # This name is in the USSD_CORE namespace
    # path("ussd/", views.ussd_callback, name="ussd_callback"),
# In urls.py
path("test-callback/", views.test_callback, name="test_callback"),
    path("mpesa-callback/", views.mpesa_callback, name="mpesa-callback"),
    path('', login_required(TemplateView.as_view(template_name='dashboard.html')), name='dashboard'),

]
