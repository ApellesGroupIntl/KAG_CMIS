from django.urls import path
from . import views

urlpatterns = [
    path("ussd/", views.ussd_callback, name="ussd_callback"),
    path("ussd_section/", views.ussd_callback_section, name="ussd_callback_section"),
    path('ussd_reg/', views.ussd_registration_view, name='ussd_registration'),
]
