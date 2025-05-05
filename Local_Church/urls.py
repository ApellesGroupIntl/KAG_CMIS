# local_church/urls.py
from django.urls import path
from .views import generate_monthly_report
from .views import monthly_report_view


urlpatterns = [
    path('generate-report/<str:month>/<int:year>/', generate_monthly_report, name='generate_monthly_report'),
    path('report/<int:report_id>/', monthly_report_view, name='monthly_report'),

]
