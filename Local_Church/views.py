# local_church/views.py

from django.shortcuts import render
from datetime import datetime
from django.db.models import Sum
from .models import Report, Attendance, Cash_Transactions  # or Giving
from django.shortcuts import render, get_object_or_404
from .models import Report

def monthly_report_view(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    return render(request, 'local_church/monthly_report.html', {'report': report})

def generate_monthly_report(request, month, year):
    # Convert month name to number if needed
    month_int = datetime.strptime(month, "%B").month
    start_date = datetime(year, month_int, 1)
    if month_int == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month_int + 1, 1)

    # Attendance Summary
    attendances = Attendance.objects.filter(date__range=(start_date, end_date))
    total_men = attendances.aggregate(Sum('men'))['men__sum'] or 0
    total_women = attendances.aggregate(Sum('women'))['women__sum'] or 0
    total_children = attendances.aggregate(Sum('children'))['children__sum'] or 0
    total_attendance = total_men + total_women + total_children

    # Giving Summary
    transactions = Cash_Transactions.objects.filter(date__range=(start_date, end_date))
    tithe = transactions.filter(Txn_type='Tithe').aggregate(Sum('Amount'))['Amount__sum'] or 0
    offering = transactions.filter(Txn_type='Offering').aggregate(Sum('Amount'))['Amount__sum'] or 0
    other_giving = transactions.exclude(Txn_type__in=['Tithe', 'Offering']).aggregate(Sum('Amount'))['Amount__sum'] or 0
    total_giving = tithe + offering + other_giving

    # Save report (optional or just render it)
    report = Report.objects.create(
        month=month,
        year=year,
        total_men=total_men,
        total_women=total_women,
        total_children=total_children,
        total_attendance=total_attendance,
        tithe_amount=tithe,
        offering_amount=offering,
        other_giving=other_giving,
        total_giving=total_giving,
    )

    return render(request, 'reports/monthly_report.html', {'report': report})
from django.shortcuts import render

# Create your views here.
