#
# Local_Church/urls.py
from django.urls import path
from . import views

app_name = "Local_Church"

urlpatterns = [
    # Dashboard
    path('', views.local_church_dashboard, name='dashboard'),

    # Reports
    path('reports/', views.report_list, name='report_list'),
    # path('reports/generate/', views.generate_report, name='generate_report'),
    path('reports/<int:pk>/', views.report_detail, name='report_detail'),
    path('reports/<int:pk>/approve/', views.approve_report, name='approve_report'),
    path('reports/generate/', views.generate_report_view, name='generate_report'),

    path('reports/generate/<int:month>/<int:year>/', views.generate_report, name='generate_report_quick'),# Add this line

    # Financial Records
    path('ussd-transactions/', views.ussd_transactions, name='ussd_transactions'),

    # Cash Transactions
    path('cash-transactions/', views.cash_transactions, name='cash_transactions'),
    path('cash-transactions/create/', views.cash_transaction_create, name='cash_transaction_create'),
    path('cash-transactions/<int:pk>/edit/', views.cash_transaction_edit, name='cash_transaction_edit'),
    path('cash-transactions/<int:pk>/delete/', views.cash_transaction_delete, name='cash_transaction_delete'),

    # Mission Offerings - FIXED THE NAMES
    path('mission-offerings/', views.mission_offerings, name='mission_offerings'),
    path('mission-offerings/create/', views.mission_offering_create, name='mission_offering_create'),
    path('mission-offerings/<int:pk>/edit/', views.mission_offering_edit, name='mission_offering_edit'),
    path('mission-offerings/<int:pk>/delete/', views.mission_offering_delete, name='mission_offering_delete'),

    # Big Days
    path('big-days/', views.big_days, name='big_days'),
    path('big-days/create/', views.big_day_create, name='big_day_create'),
    path('big-days/<int:pk>/edit/', views.big_day_edit, name='big_day_edit'),
    path('big-days/<int:pk>/delete/', views.big_day_delete, name='big_day_delete'),

    # Plot Buying
    path('plot-buying/', views.plot_buying, name='plot_buying'),
    path('plot-buying/create/', views.plot_buying_create, name='plot_buying_create'),
    path('plot-buying/<int:pk>/edit/', views.plot_buying_edit, name='plot_buying_edit'),
    path('plot-buying/<int:pk>/delete/', views.plot_buying_delete, name='plot_buying_delete'),

    # People Management
    path('attendance/', views.attendance_list, name='attendance'),
    path('attendance/create/', views.attendance_create, name='attendance_create'),
    path('attendance/<int:pk>/edit/', views.attendance_edit, name='attendance_edit'),
    path('attendance/<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),

    path('visitors/', views.visitors_list, name='visitors'),
    path('visitors/create/', views.visitor_create, name='visitor_create'),
    path('visitors/<int:pk>/edit/', views.visitor_edit, name='visitor_edit'),
    path('visitors/<int:pk>/delete/', views.visitor_delete, name='visitor_delete'),

    # Operations
    path('expenses/', views.expenses_list, name='expenses'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),

    path('missions/', views.missions_list, name='missions'),
    path('missions/create/', views.mission_create, name='mission_create'),
    path('missions/<int:pk>/edit/', views.mission_edit, name='mission_edit'),
    path('missions/<int:pk>/delete/', views.mission_delete, name='mission_delete'),

    # Placeholder
    path('placeholder/', views.placeholder_view, name='placeholder'),
]
