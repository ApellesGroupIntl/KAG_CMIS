# views.py
from calendar import month_name

from django.utils import timezone  # This is the correct import
from django.contrib import messages  # This must be at the top
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Report, USSD_Transactions, Visitors
# from .forms import forms
from .utils import generate_monthly_report
# Local_Church/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from .models import (
    USSD_Transactions, Cash_Transactions, Mission_Offering,
    Big_Day, Plot_Buying, Attendance, Visitors, Expenses, Missions, Report
)
from .forms import (
    CashTransactionForm, MissionOfferingForm, BigDayForm, PlotBuyingForm,
    AttendanceForm, VisitorForm, ExpenseForm, MissionForm, ReportFilterForm
)
from django import forms
from . import models


class ReportFilterForm(forms.Form):
    church = forms.ChoiceField(choices=[], required=False)
    month = forms.ChoiceField(choices=[], required=False)
    year = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate choices dynamically
        self.fields['church'].choices = self.get_church_choices()
        self.fields['month'].choices = self.get_month_choices()
        self.fields['year'].choices = self.get_year_choices()

    def get_church_choices(self):
        # Get unique church names from your database
        from .models import Report
        churches = Report.objects.values_list('church_name', flat=True).distinct()
        return [('', 'All Churches')] + [(church, church) for church in churches]

    def get_month_choices(self):
        months = [
            (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
            (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
            (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
        ]
        return [('', 'All Months')] + months

    def get_year_choices(self):
        # Get unique years from your database
        from .models import Report
        years = Report.objects.values_list('year', flat=True).distinct()
        return [('', 'All Years')] + [(year, year) for year in sorted(years, reverse=True)]

# In views.py, update the create and edit views to handle the raw form data
@login_required
def cash_transaction_create(request):
    if request.method == 'POST':
        try:
            transaction = Cash_Transactions.objects.create(
                date=request.POST.get('date'),
                Tithe=request.POST.get('Tithe', 0) or 0,
                Main_Service_Offering=request.POST.get('Main_Service_Offering', 0) or 0,
                Mid_Week_Service_Offering=request.POST.get('Mid_Week_Service_Offering', 0) or 0,
                Children_Offering=request.POST.get('Children_Offering', 0) or 0,
                Youths_Offering=request.POST.get('Youths_Offering', 0) or 0,
  # Fixed: Youth_Offering instead of Youths_Offering
                Teens_Offering=request.POST.get('Teens_Offering', 0) or 0,
                church_name=request.POST.get('church_name')
            )
            messages.success(request, 'Cash transaction added successfully!')
            return redirect('Local_Church:cash_transactions')
        except Exception as e:
            messages.error(request, f'Error creating transaction: {str(e)}')
            return redirect('Local_Church:cash_transactions')

    return redirect('Local_Church:cash_transactions')

@login_required
def cash_transaction_edit(request, pk):
    transaction = get_object_or_404(Cash_Transactions, pk=pk)
    if request.method == 'POST':
        try:
            transaction.date = request.POST.get('date')
            transaction.Tithe = request.POST.get('Tithe', 0) or 0
            transaction.Main_Service_Offering = request.POST.get('Main_Service_Offering', 0) or 0
            transaction.Mid_Week_Service_Offering = request.POST.get('Mid_Week_Service_Offering', 0) or 0
            transaction.Children_Offering = request.POST.get('Children_Offering', 0) or 0
            transaction.Youths_Offering = request.POST.get('Youths_Offering', 0) or 0
            transaction.Teens_Offering = request.POST.get('Teens_Offering', 0) or 0
            transaction.church_name = request.POST.get('church_name')
            transaction.save()
            return redirect('Local_Church:cash_transactions')
        except Exception as e:
            # Handle error
            return redirect('Local_Church:cash_transactions')

    return redirect('Local_Church:cash_transactions')


@login_required
def cash_transaction_delete(request, pk):
    transaction = get_object_or_404(Cash_Transactions, pk=pk)
    if request.method == 'POST':
        transaction.delete()
        return redirect('Local_Church:cash_transactions')

    return render(request, 'Local_Church/confirm_delete.html', {
        'object': transaction,
        'title': 'Delete Cash Transaction'
    })

# Mission Offering CRUD
@login_required
def mission_offering_create(request):
    if request.method == 'POST':
        try:
            offering = Mission_Offering.objects.create(
                date=request.POST.get('date'),
                Amount=request.POST.get('Amount', 0) or 0,
                church_name=request.POST.get('church_name')
            )
            return redirect('Local_Church:mission_offerings')
        except Exception as e:
            return redirect('Local_Church:mission_offerings')

    return redirect('Local_Church:mission_offerings')


@login_required
def mission_offering_edit(request, pk):
    offering = get_object_or_404(Mission_Offering, pk=pk)
    if request.method == 'POST':
        try:
            offering.date = request.POST.get('date')
            offering.Amount = request.POST.get('Amount', 0) or 0
            offering.church_name = request.POST.get('church_name')
            offering.save()
            return redirect('Local_Church:mission_offerings')
        except Exception as e:
            return redirect('Local_Church:mission_offerings')

    return redirect('Local_Church:mission_offerings')


@login_required
def mission_offering_delete(request, pk):
    offering = get_object_or_404(Mission_Offering, pk=pk)
    if request.method == 'POST':
        offering.delete()
        return redirect('Local_Church:mission_offerings')

    return render(request, 'Local_Church/confirm_delete.html', {
        'object': offering,
        'title': 'Delete Mission Offering'
    })


# Big Day CRUD
@login_required
def big_day_create(request):
    if request.method == 'POST':
        form = BigDayForm(request.POST)
        if form.is_valid():
            big_day = form.save()
            return redirect('Local_Church:big_days')
    else:
        form = BigDayForm()

    return render(request, 'Local_Church/big_day_form.html', {
        'form': form,
        'title': 'Add Big Day',
        'action': 'Create'
    })


@login_required
def big_day_edit(request, pk):
    big_day = get_object_or_404(Big_Day, pk=pk)
    if request.method == 'POST':
        form = BigDayForm(request.POST, instance=big_day)
        if form.is_valid():
            form.save()
            return redirect('Local_Church:big_days')
    else:
        form = BigDayForm(instance=big_day)

    return render(request, 'Local_Church/big_day_form.html', {
        'form': form,
        'title': 'Edit Big Day',
        'action': 'Update'
    })


@login_required
def big_day_delete(request, pk):
    big_day = get_object_or_404(Big_Day, pk=pk)
    if request.method == 'POST':
        big_day.delete()
        return redirect('Local_Church:big_days')

    return render(request, 'Local_Church/confirm_delete.html', {
        'object': big_day,
        'title': 'Delete Big Day'
    })


# Plot Buying CRUD
@login_required
def plot_buying_create(request):
    if request.method == 'POST':
        form = PlotBuyingForm(request.POST)
        if form.is_valid():
            plot = form.save()
            return redirect('Local_Church:plot_buying')
    else:
        form = PlotBuyingForm()

    return render(request, 'Local_Church/plot_buying_form.html', {
        'form': form,
        'title': 'Add Plot Buying',
        'action': 'Create'
    })


@login_required
def plot_buying_edit(request, pk):
    plot = get_object_or_404(Plot_Buying, pk=pk)
    if request.method == 'POST':
        form = PlotBuyingForm(request.POST, instance=plot)
        if form.is_valid():
            form.save()
            return redirect('Local_Church:plot_buying')
    else:
        form = PlotBuyingForm(instance=plot)

    return render(request, 'Local_Church/plot_buying_form.html', {
        'form': form,
        'title': 'Edit Plot Buying',
        'action': 'Update'
    })


@login_required
def plot_buying_delete(request, pk):
    plot = get_object_or_404(Plot_Buying, pk=pk)
    if request.method == 'POST':
        plot.delete()
        return redirect('Local_Church:plot_buying')

    return render(request, 'Local_Church/confirm_delete.html', {
        'object': plot,
        'title': 'Delete Plot Buying'
    })


# Attendance CRUD
@login_required
def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save()
            return redirect('Local_Church:attendance')
    else:
        form = AttendanceForm()

    return render(request, 'Local_Church/attendance_form.html', {
        'form': form,
        'title': 'Add Attendance',
        'action': 'Create'
    })


@login_required
def attendance_edit(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            return redirect('Local_Church:attendance')
    else:
        form = AttendanceForm(instance=attendance)

    return render(request, 'Local_Church/attendance_form.html', {
        'form': form,
        'title': 'Edit Attendance',
        'action': 'Update'
    })


@login_required
def attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        attendance.delete()
        return redirect('Local_Church:attendance')

    return render(request, 'Local_Church/confirm_delete.html', {
        'object': attendance,
        'title': 'Delete Attendance'
    })


# Visitors CRUD
@login_required
def visitor_create(request):
    if request.method == 'POST':
        form = VisitorForm(request.POST)
        if form.is_valid():
            visitor = form.save()
            return redirect('Local_Church:visitors')
    else:
        form = VisitorForm()

    return render(request, 'Local_Church/visitor_form.html', {
        'form': form,
        'title': 'Add Visitor',
        'action': 'Create'
    })


@login_required
def visitor_edit(request, pk):
    visitor = get_object_or_404(Visitors, pk=pk)
    if request.method == 'POST':
        form = VisitorForm(request.POST, instance=visitor)
        if form.is_valid():
            form.save()
            return redirect('Local_Church:visitors')
    else:
        form = VisitorForm(instance=visitor)

    return render(request, 'Local_Church/visitor_form.html', {
        'form': form,
        'title': 'Edit Visitor',
        'action': 'Update'
    })


@login_required
def visitor_delete(request, pk):
    visitor = get_object_or_404(Visitors, pk=pk)
    if request.method == 'POST':
        visitor.delete()
        return redirect('Local_Church:visitors')

    return render(request, 'Local_Church/confirm_delete.html', {
        'object': visitor,
        'title': 'Delete Visitor'
    })


# Expenses CRUD
@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save()
            return redirect('Local_Church:expenses')
    else:
        form = ExpenseForm()

    return render(request, 'Local_Church/expense_form.html', {
        'form': form,
        'title': 'Add Expense',
        'action': 'Create'
    })


@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expenses, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('Local_Church:expenses')
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'Local_Church/expense_form.html', {
        'form': form,
        'title': 'Edit Expense',
        'action': 'Update'
    })


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expenses, pk=pk)
    if request.method == 'POST':
        expense.delete()
        return redirect('Local_Church:expenses')

    return render(request, 'Local_Church/confirm_delete.html', {
        'object': expense,
        'title': 'Delete Expense'
    })


# Missions CRUD
@login_required
def mission_create(request):
    if request.method == 'POST':
        form = MissionForm(request.POST)
        if form.is_valid():
            mission = form.save()
            return redirect('Local_Church:missions')
    else:
        form = MissionForm()

    return render(request, 'Local_Church/mission_form.html', {
        'form': form,
        'title': 'Add Mission',
        'action': 'Create'
    })


@login_required
def mission_edit(request, pk):
    mission = get_object_or_404(Missions, pk=pk)
    if request.method == 'POST':
        form = MissionForm(request.POST, instance=mission)
        if form.is_valid():
            form.save()
            return redirect('Local_Church:missions')
    else:
        form = MissionForm(instance=mission)

    return render(request, 'Local_Church/mission_form.html', {
        'form': form,
        'title': 'Edit Mission',
        'action': 'Update'
    })


@login_required
def mission_delete(request, pk):
    mission = get_object_or_404(Missions, pk=pk)
    if request.method == 'POST':
        mission.delete()
        return redirect('Local_Church:missions')

    return render(request, 'Local_Church/confirm_delete.html', {
        'object': mission,
        'title': 'Delete Mission'
    })

# Dashboard View
@login_required
def local_church_dashboard(request):
    try:
        # Get counts for dashboard cards
        reports_count = Report.objects.count()
        total_giving = Report.objects.aggregate(total=Sum('total_givings'))['total'] or 0

        # Calculate total attendance from all reports
        total_attendance = (Report.objects.aggregate(
            total=Sum('attendance_Men') +
                  Sum('attendance_Women') +
                  Sum('attendance_Youth') +
                  Sum('attendance_Teens') +
                  Sum('attendance_Children')
        )['total'] or 0)

        visitors_count = Visitors.objects.count()

        # Get recent activity
        recent_reports = Report.objects.order_by('-generated_on')[:3]
        recent_activity = []

        for report in recent_reports:
            recent_activity.append({
                'type': 'Report',
                'badge_type': 'primary',
                'description': f'{report.church_name} - {report.month} {report.year}',
                'date': report.generated_on,
                'amount': report.total_givings
            })

    except Exception as e:
        # Handle case where models don't exist or there are no records
        reports_count = 0
        total_giving = 0
        total_attendance = 0
        visitors_count = 0
        recent_activity = []

    context = {
        'reports_count': reports_count,
        'total_giving': total_giving,
        'total_attendance': total_attendance,
        'visitors_count': visitors_count,
        'recent_activity': recent_activity,
    }

    return render(request, 'Local_Church/dashboard.html', context)

@login_required
def report_list(request):
    # form = ReportFilterForm(request.GET or None
    form = ReportFilterForm()  # No arguments
    reports = Report.objects.all().order_by('-year', '-month')

    if form.is_valid():
        church = form.cleaned_data.get('church')
        month = form.cleaned_data.get('month')
        year = form.cleaned_data.get('year')

        if church:
            reports = reports.filter(church_name=church)
        if month:
            reports = reports.filter(month=month)
        if year:
            reports = reports.filter(year=year)

    context = {
        'reports': reports,
        'form': form,
    }
    return render(request, 'Local_Church/report_list.html', context)

@login_required
def report_detail(request, pk):
    report = get_object_or_404(Report, pk=pk)
    return render(request, 'Local_Church/report_detail.html', {'report': report})


def generate_report(church, month, year, start_date=None, end_date=None, missions_data=None, cash_data=None,
                    attendance_data=None):
    """
    Generate a comprehensive monthly report that matches your Report model structure
    """
    # ... [previous code remains the same] ...

    # Aggregate expenses
    expense_categories = Expenses.objects.filter(
        church_name=church,
        date__gte=start_date,
        date__lt=end_date
    ).values('Expense_Name').annotate(
        category_total=Sum('Expense_Amount')
    ).order_by('-category_total')

    # Create expense breakdown string
    expense_breakdown = ""
    for category in expense_categories:
        expense_breakdown += f"{category['Expense_Name']}: Ksh {category['category_total'] or 0:.2f}, "

    # Remove trailing comma and space
    if expense_breakdown:
        expense_breakdown = expense_breakdown[:-2]

    # Aggregate total expenses
    expenses_data = Expenses.objects.filter(
        church_name=church,
        date__gte=start_date,
        date__lt=end_date
    ).aggregate(
        total_expenses=Sum('Expense_Amount')
    )

    # Count visitors
    visitors_count = Visitors.objects.filter(
        church_name=church,
        date__gte=start_date,
        date__lt=end_date
    ).count()

    # Calculate individual components (KEEP THEM SEPARATE)
    total_tithes = cash_data['total_tithe'] or 0
    total_offerings = (cash_data['total_offering'] or 0) + (cash_data['total_midweek'] or 0)
    total_youth_offerings = cash_data['total_youth'] or 0
    total_children_offerings = cash_data['total_children'] or 0

    # Mission components - keep separate
    mission_offerings_amount = mission_offerings['total_mission_offerings'] or 0
    mission_support_amount = missions_data['total_missions'] or 0

    # Plot and Big Days - keep separate
    plot_contributions_amount = plot_buying['total_plot'] or 0
    big_days_amount_value = big_days['total_big_days'] or 0

    # Other givings (only plot + big days)
    other_givings = plot_contributions_amount + big_days_amount_value

    # Expenses total
    expenses_total = expenses_data['total_expenses'] or 0  # Fixed variable name

    # Calculate total givings (sum of ALL income components)
    total_givings = (
        total_tithes +
        total_offerings +
        total_youth_offerings +
        total_children_offerings +
        mission_offerings_amount +
        mission_support_amount +
        other_givings
    )

    # Debug: Print all values
    print(f"Tithes: {total_tithes}")
    print(f"Offerings: {total_offerings}")
    print(f"Youth Offerings: {total_youth_offerings}")
    print(f"Children Offerings: {total_children_offerings}")
    print(f"Mission Offerings: {mission_offerings_amount}")
    print(f"Mission Support: {mission_support_amount}")
    print(f"Plot Contributions: {plot_contributions_amount}")
    print(f"Big Days Amount: {big_days_amount_value}")
    print(f"Other Givings: {other_givings}")
    print(f"Expenses: {expenses_total}")  # Fixed variable name
    print(f"Total Givings: {total_givings}")

    # Create the report with ALL fields
    report = Report.objects.create(
        month=month_name,
        year=year,
        church_name=church,
        section_name="MURANGÁ SECTION",
        district_name="MT. KENYA WEST DISTRICT",

        # Attendance data
        attendance_Men=attendance_data['total_men'] or 0,
        attendance_Women=attendance_data['total_women'] or 0,
        attendance_Youth=attendance_data['total_youth'] or 0,
        attendance_Teens=attendance_data['total_teens'] or 0,
        attendance_Children=attendance_data['total_children'] or 0,
        total_Visitors=visitors_count,

        # Financial data - ORIGINAL FIELDS
        Tithes=total_tithes,
        Offerings=total_offerings,
        Youth_Offerings=total_youth_offerings,
        Children_Offerings=total_children_offerings,
        Missions=mission_support_amount,  # Save mission support to original Missions field
        other_givings=other_givings,  # Plot + Big Days
        total_givings=total_givings,

        # NEW FIELDS - individual components
        mission_offerings=mission_offerings_amount,
        plot_contributions=plot_contributions_amount,
        big_days_amount=big_days_amount_value,
        mission_support=mission_support_amount,
        expenses=expenses_total,  # Fixed variable name
        expense_breakdown=expense_breakdown,

        # Notes
        notes=f"Mission Offerings: Ksh {mission_offerings_amount} | Plot: Ksh {plot_contributions_amount} | Big Days: Ksh {big_days_amount_value}"
    )

    print(f"Report created successfully: {report}")
    return report
# THIS IS THE VIEW FUNCTION - IT SHOULD HAVE THE DECORATOR!
@login_required
def generate_report_view(request):
    """
    This is the actual view that handles the web request
    """
    if request.method == 'POST':
        try:
            church = request.POST.get('church')
            month = request.POST.get('month')
            year = request.POST.get('year')

            # Validate inputs
            if not church or not month or not year:
                messages.error(request, "Please fill in all required fields.")
                return render(request, 'Local_Church/generate_report.html')

            # Convert to integers
            month = int(month)
            year = int(year)

            if month < 1 or month > 12:
                messages.error(request, "Please select a valid month (1-12).")
                return render(request, 'Local_Church/generate_report.html')

            # Generate the report using the function above
            report = generate_monthly_report(church, month, year)
            messages.success(request, f"Report for {church} - {month}/{year} generated successfully!")
            return redirect('Local_Church:report_detail', pk=report.pk)

        except (ValueError, TypeError):
            messages.error(request, "Invalid input values. Please enter valid numbers.")
            return render(request, 'Local_Church/generate_report.html')
        except Exception as e:
            messages.error(request, f"Error generating report: {str(e)}")
            return render(request, 'Local_Church/generate_report.html')

    # GET request - show the form
    return render(request, 'Local_Church/generate_report.html')


@login_required
def approve_report(request, pk):
    report = get_object_or_404(Report, pk=pk)

    if request.method == 'POST':
        if report.is_approved:
            messages.warning(request, "This report is already approved.")
            return redirect('Local_Church:report_detail', pk=report.pk)

        # Save the user's full name instead of username
        full_name = request.user.get_full_name()
        if not full_name.strip():  # If no full name, use username
            full_name = request.user.username

        report.is_approved = True
        report.approved_by = full_name
        report.approved_on = timezone.now()
        report.save()

        messages.success(request, f"Report for {report.month} {report.year} has been approved successfully!")
        return redirect('Local_Church:report_detail', pk=report.pk)

    messages.error(request, "Invalid request method.")
    return redirect('Local_Church:report_detail', pk=report.pk)
# def approve_report(request, pk):
#     # Check if user has permission to approve reports
#     if not request.user.has_perm('Local_Church.can_approve_reports'):
#         messages.error(request, "You don't have permission to approve reports.")
#         return redirect('Local_Church:report_detail', pk=pk)
#
#     report = get_object_or_404(Report, pk=pk)
#
#     if request.method == 'POST':
#         if report.is_approved:
#             messages.warning(request, "This report is already approved.")
#             return redirect('Local_Church:report_detail', pk=report.pk)
#
#         report.is_approved = True
#         report.approved_by = request.user
#         report.approved_on = timezone.now()
#         report.save()
#
#         messages.success(request, f"Report for {report.month}/{report.year} has been approved successfully!")
#         return redirect('Local_Church:report_detail', pk=report.pk)
#
#     messages.error(request, "Invalid request method.")
#     return redirect('Local_Church:report_detail', pk=report.pk)
# # Report Views
# @login_required
# def report_list(request):
#     reports = Report.objects.all().order_by('-year', '-month')
#
#     # Filtering
#     church = request.GET.get('church')
#     month = request.GET.get('month')
#     year = request.GET.get('year')
#
#     if church:
#         reports = reports.filter(church_name=church)
#     if month:
#         reports = reports.filter(month=month)
#     if year:
#         reports = reports.filter(year=year)
#
#     paginator = Paginator(reports, 20)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#
#     context = {
#         'reports': page_obj,
#         'title': 'Monthly Reports',
#     }
#     return render(request, 'Local_Church/report_list.html', context)
#
#
# @login_required
# def report_detail(request, pk):
#     report = get_object_or_404(Report, pk=pk)
#     # Add calculated fields for the template
#     total_attendance = report.get_attendance_total()
#     report.average_per_member = report.total_givings / total_attendance if total_attendance > 0 else 0
#     report.tithe_percentage = (report.Tithes / report.total_givings * 100) if report.total_givings > 0 else 0
#
#     context = {
#         'report': report,
#         'title': f'Report - {report.month} {report.year}',
#     }
#     return render(request, 'Local_Church/report_detail.html', context)
#
#
# @login_required
# def generate_report(request):
#     if request.method == 'POST':
#         church = request.POST.get('church')
#         month = int(request.POST.get('month'))
#         year = int(request.POST.get('year'))
#
#         report = generate_monthly_report(church, month, year)
#         return redirect('Local_Church:report_detail', pk=report.pk)
#
#     return render(request, 'Local_Church/generate_report.html', {
#         'title': 'Generate Report'
#     })


# USSD Transactions
@login_required
def ussd_transactions(request):
    transactions = USSD_Transactions.objects.all().order_by('-Timestamp')

    # Filtering
    txn_type = request.GET.get('txn_type')
    church = request.GET.get('church')
    phone = request.GET.get('phone')

    if txn_type:
        transactions = transactions.filter(Txn_type__icontains=txn_type)
    if church:
        transactions = transactions.filter(church_name=church)
    if phone:
        transactions = transactions.filter(Phone_number__icontains=phone)

    # Pagination
    paginator = Paginator(transactions, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_amount = transactions.aggregate(total=Sum('Amount'))['total'] or 0

    context = {
        'transactions': page_obj,
        'total_amount': total_amount,
        'title': 'USSD Transactions',
    }
    return render(request, 'Local_Church/ussd_transactions.html', context)


# Cash Transactions
@login_required
def cash_transactions(request):
    transactions = Cash_Transactions.objects.all().order_by('-date')

    # Filtering
    church = request.GET.get('church')
    if church:
        transactions = transactions.filter(church_name=church)

    # Pagination
    paginator = Paginator(transactions, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Totals
    totals = transactions.aggregate(
        total_tithe=Sum('Tithe'),
        total_main_offering=Sum('Main_Service_Offering'),
        total_midweek=Sum('Mid_Week_Service_Offering'),
        total_children=Sum('Children_Offering'),
        total_youths=Sum('Youths_Offering'),
        total_teens=Sum('Teens_Offering')
    )

    context = {
        'transactions': page_obj,
        'totals': totals,
        'title': 'Cash Transactions',
    }
    return render(request, 'Local_Church/cash_transactions.html', context)


# Mission Offerings
@login_required
def mission_offerings(request):
    offerings = Mission_Offering.objects.all().order_by('-date')

    # Filtering
    church = request.GET.get('church')
    if church:
        offerings = offerings.filter(church_name=church)

    paginator = Paginator(offerings, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_amount = offerings.aggregate(total=Sum('Amount'))['total'] or 0

    context = {
        'offerings': page_obj,
        'total_amount': total_amount,
        'title': 'Mission Offerings',
    }
    return render(request, 'Local_Church/mission_offerings.html', context)


# Big Days
@login_required
def big_days(request):
    big_days = Big_Day.objects.all().order_by('-date')

    # Filtering
    church = request.GET.get('church')
    event_type = request.GET.get('event_type')

    if church:
        big_days = big_days.filter(church_name=church)
    if event_type:
        big_days = big_days.filter(Big_Day=event_type)

    paginator = Paginator(big_days, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_amount = big_days.aggregate(total=Sum('Amount'))['total'] or 0

    context = {
        'big_days': page_obj,
        'total_amount': total_amount,
        'title': 'Big Days',
    }
    return render(request, 'Local_Church/big_days.html', context)


# Plot Buying
@login_required
def plot_buying(request):
    plots = Plot_Buying.objects.all().order_by('-date')

    # Filtering
    church = request.GET.get('church')
    if church:
        plots = plots.filter(church_name=church)

    paginator = Paginator(plots, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_amount = plots.aggregate(total=Sum('Amount'))['total'] or 0

    context = {
        'plots': page_obj,
        'total_amount': total_amount,
        'title': 'Plot Buying',
    }
    return render(request, 'Local_Church/plot_buying.html', context)


# Attendance
@login_required
def attendance_list(request):
    attendance_records = Attendance.objects.all().order_by('-date')

    # Filtering
    church = request.GET.get('church')
    if church:
        attendance_records = attendance_records.filter(church_name=church)

    paginator = Paginator(attendance_records, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculate totals
    totals = attendance_records.aggregate(
        total_men=Sum('Men'),
        total_women=Sum('Ladies'),
        total_youth=Sum('Youths'),
        total_teens=Sum('Teens'),
        total_children=Sum('Children')
    )

    context = {
        'attendance_records': page_obj,
        'totals': totals,
        'title': 'Attendance Records',
    }
    return render(request, 'Local_Church/attendance_list.html', context)


# Visitors
@login_required
def visitors_list(request):
    visitors = Visitors.objects.all().order_by('-date')

    # Filtering
    church = request.GET.get('church')
    name = request.GET.get('name')

    if church:
        visitors = visitors.filter(church_name=church)
    if name:
        visitors = visitors.filter(Name__icontains=name)

    paginator = Paginator(visitors, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_visitors = visitors.count()

    context = {
        'visitors': page_obj,
        'total_visitors': total_visitors,
        'title': 'Visitors',
    }
    return render(request, 'Local_Church/visitors_list.html', context)


# Expenses
@login_required
def expenses_list(request):
    expenses = Expenses.objects.all().order_by('-date')

    # Filtering
    church = request.GET.get('church')
    approved = request.GET.get('approved')
    approved_count = expenses.filter(Expense_Approved=True).count()
    pending_count = expenses.filter(Expense_Approved=False).count()

    if church:
        expenses = expenses.filter(church_name=church)
    if approved:
        expenses = expenses.filter(Expense_Approved=approved.lower() == 'true')

    paginator = Paginator(expenses, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_amount = expenses.aggregate(total=Sum('Expense_Amount'))['total'] or 0
    approved_amount = expenses.filter(Expense_Approved=True).aggregate(total=Sum('Expense_Amount'))['total'] or 0

    context = {
        'expenses': page_obj,
        'total_amount': total_amount,
        'approved_amount': approved_amount,
        'title': 'Expenses',
        'approved_count': approved_count,
        'pending_count': pending_count,
    }
    return render(request, 'Local_Church/expenses_list.html', context)


# Missions
@login_required
def missions_list(request):
    missions = Missions.objects.all().order_by('-date')

    # Filtering
    church = request.GET.get('church')
    missionary = request.GET.get('missionary')


    if church:
        missions = missions.filter(church_name=church)
    if missionary:
        missions = missions.filter(Missionary_Name__icontains=missionary)

    paginator = Paginator(missions, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_amount = missions.aggregate(total=Sum('Total_amount'))['total'] or 0

    context = {
        'missions': page_obj,
        'total_amount': total_amount,
        'title': 'Missions',
    }
    return render(request, 'Local_Church/missions_list.html', context)


# Placeholder view for any missing functionality
@login_required
def placeholder_view(request, title="Page", message="This page is under construction"):
    return render(request, 'Local_Church/placeholder.html', {
        'title': title,
        'message': message
    })





