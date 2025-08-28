from django.urls import path
from . import views

urlpatterns = [
    path("validation/", views.mpesa_validation, name="mpesa_validation"),
    path("confirmation/", views.mpesa_confirmation, name="mpesa_confirmation"),
    path("callback/", views.mpesa_callback, name="mpesa_callback"),
]



# from django.urls import path
# from . import views
# # mpesa/urls.py
# from django.urls import path
# from .views import mpesa_callback
#
# urlpatterns = [
#     path("validation/", views.mpesa_validation),
#     path("confirmation/", views.mpesa_confirmation),
#     path('callback/', mpesa_callback, name='mpesa_callback'),
#     path('api/mpesa/callback/', mpesa_callback, name='mpesa_callback'),
#
# ]
