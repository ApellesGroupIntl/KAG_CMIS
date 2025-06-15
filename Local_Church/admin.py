from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from django.contrib import messages
from .models import USSD_Transactions, Attendance, Cash_Transactions, Expenses, Plot_Buying, Mission_Offering, Big_Day, Report, Missions, Visitors  # or whatever model you created
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Report
from .utils import generate_monthly_report
from datetime import datetime
# admin.site.register(USSD_Transactions)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'church_name',
        'month_year',
        'attendance_summary',
        'financial_summary',
        'is_approved',
        'generated_on'
    )
    list_filter = ('church_name', 'month', 'year', 'is_approved')
    search_fields = ('church_name', 'month', 'year', 'notes')
    actions = ['generate_reports', 'approve_reports']
    readonly_fields = ('generated_on', 'last_updated')

    fieldsets = (
        ('Basic Information', {
            'fields': ('month', 'year', 'church_name', 'section_name', 'district_name')
        }),
        ('Attendance', {
            'fields': (
                'attendance_Men',
                'attendance_Women',
                'attendance_Youth',
                'attendance_Teens',
                'attendance_Children',
                'total_Visitors'
            )
        }),
        ('Financials', {
            'fields': (
                'Tithes',
                'Offerings',
                'Youth_Offerings',
                'Children_Offerings',
                'Missions',
                'other_givings',
                'total_givings'
            )
        }),
        ('Approval', {
            'fields': ('is_approved', 'approved_by', 'notes')
        }),
        ('Metadata', {
            'fields': ('generated_on', 'last_updated')
        }),
    )

    def month_year(self, obj):
        return f"{obj.month} {obj.year}"
    month_year.short_description = 'Period'

    def attendance_summary(self, obj):
        return f"M: {obj.attendance_Men} | W: {obj.attendance_Women} | Y: {obj.attendance_Youth}"
    attendance_summary.short_description = 'Attendance'

    def financial_summary(self, obj):
        return f"Total: {obj.total_givings}"
    financial_summary.short_description = 'Finances'

    def generate_reports(self, request, queryset):
        for report in queryset:
            generate_monthly_report(
                report.church_name,
                datetime.strptime(report.month, "%B").month,
                report.year
            )
        self.message_user(request, "Selected reports have been regenerated.")
    generate_reports.short_description = "Regenerate selected reports"

    def approve_reports(self, request, queryset):
        updated = queryset.update(is_approved=True, approved_by=request.user.get_full_name())
        self.message_user(request, f"{updated} reports have been approved.")
    approve_reports.short_description = "Approve selected reports"


class USSD_TransactionsAdmin(admin.ModelAdmin):
    list_display = ['date', 'week_of_month', 'Txn_code', 'Phone_number', 'Txn_type', 'Amount', 'Month', 'Timestamp' ]
    search_fields = ['Txn_type', 'week_of_month', 'Txn_code', 'Phone_number', 'Month']
    list_filter = ['Txn_type', 'week_of_month']

    def changelist_view(self, request, extra_context=None):
        # Total amount for all records in the database (without any filter applied)
        total_amount_all = self.model.objects.aggregate(total=Sum('Amount'))['total'] or 0

        # Total amount for the filtered queryset (based on applied filters)
        queryset = self.get_queryset(request)
        total_amount_filtered = queryset.aggregate(total=Sum('Amount'))['total'] or 0

        # Initialize extra_context if it's None
        if extra_context is None:
            extra_context = {}

        # Add the totals to the extra_context
        extra_context['total_amount_all'] = total_amount_all
        extra_context['total_amount_filtered'] = total_amount_filtered

        print("Extra Context Passed:", extra_context)  # Check if it's now populated

        # Return the view with the updated context
        return super().changelist_view(request, extra_context=extra_context)


admin.site.register(USSD_Transactions, USSD_TransactionsAdmin)

class Cash_TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'week_of_month', 'Tithe', 'Main_Service_Offering', 'Mid_Week_Service_Offering', 'Children_Offering', 'Youths_Offering', 'Teens_Offering']
    search_fields = ['date', 'week_of_month', 'Main_Service_Offering', 'Mid_Week_Service_Offering', 'Tithe']
    list_filter = ['date', 'week_of_month', ]
admin.site.register(Cash_Transactions, Cash_TransactionAdmin)

class Plot_BuyingAdmin(admin.ModelAdmin):
    list_display = ['date', 'Amount']
    search_fields = ['date', 'Amount']
    list_filter = ['date']
admin.site.register(Plot_Buying, Plot_BuyingAdmin)

class Mission_OfferingAdmin(admin.ModelAdmin):
    list_display = ['date', 'Amount']
    search_fields = ['date', 'Amount']
    list_filter = ['date']
admin.site.register(Mission_Offering, Mission_OfferingAdmin)

class MissionsAdmin(admin.ModelAdmin):
    list_display = ['date', "KAGDOM_Contribution", "District_Mission_Contribution", "Monthly_Support", "Missionary_Name", "Total_amount", "church_name"]
    search_fields = ['KAGDOM_Contribution', "District_Mission_Contribution", "Monthly_Support", "Missionary_Name"]

admin.site.register(Missions, MissionsAdmin)


class Big_DayAdmin(admin.ModelAdmin):
    list_display = ['date', 'Big_Day', 'week_of_month','Amount']
    search_fields = ['date', 'Amount']
    list_filter = ['date', 'Big_Day', 'week_of_month']
admin.site.register(Big_Day, Big_DayAdmin)


class ExpensesAdmin(admin.ModelAdmin):
    list_display = ['date', 'week_of_month', 'Expense_Name', 'Expense_Amount', 'Expense_Approved']
    search_fields = ['date', 'week_of_month', 'Expense_Name']
    list_filter = ['date', 'week_of_month', 'Expense_Name', 'Expense_Amount', 'Expense_Approved']

# Register the model with the admin site
admin.site.register(Expenses, ExpensesAdmin)


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['date', 'week_of_month', 'Children', 'Teens', 'Youths', 'Ladies', 'Men']
    search_fields = ['date', 'week_of_month']
    list_filter = ['date', 'week_of_month', 'Children', 'Teens', 'Youths', 'Ladies', 'Men']

# Register the model with the admin site
admin.site.register(Attendance, AttendanceAdmin)

class VisitorsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'week_of_month', 'Name', 'Main_Service',
        'Mid_Week_Service', 'Phone_number', 'Area_of_residence', 'Fellowship_again', 'Reason_for_visit'
    ]
    search_fields = ['Name', 'Phone_number', 'Area_of_residence']
    list_filter = ['date', 'week_of_month', 'Main_Service', 'Mid_Week_Service', 'Fellowship_again']
    ordering = ['-date']  # Most recent first
    def phone_link(self, obj):
        return format_html('<a href="tel:{}">{}</a>', obj.Phone_number, obj.Phone_number)

    phone_link.short_description = "Phone Number"

admin.site.register(Visitors, VisitorsAdmin)
