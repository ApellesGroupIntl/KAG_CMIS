from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from django.contrib import messages
from .models import USSD_Transactions, Attendance, Cash_Transactions, Plot_Buying, Mission_Offering, Big_Day, Report, Visitors  # or whatever model you created

# admin.site.register(USSD_Transactions)
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('church_name', 'tithes', 'offerings', 'missions', 'total_givings', 'pastor_name', 'generated_on')
    list_filter = ('church_name', 'generated_on')
    search_fields = ('church_name', 'total_givings')
    ordering = ('-generated_on',)

class USSD_TransactionsAdmin(admin.ModelAdmin):
    list_display = ['date', 'week_of_month', 'Txn_code', 'Phone_number', 'Txn_type', 'Amount', 'Month', 'Timestamp' ]
    search_fields = ['Txn_type', 'week_of_month', 'Txn_code', 'Phone_number']
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
    search_fields = ['date', 'week_of_month', 'Main_Service_Offering', 'Mid_Week_Service_Offering']
    list_filter = ['date', 'week_of_month']
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

class Big_DayAdmin(admin.ModelAdmin):
    list_display = ['date', 'Amount']
    search_fields = ['date', 'Amount']
    list_filter = ['date']
admin.site.register(Big_Day, Big_DayAdmin)

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['date', 'week_of_month', 'Children', 'Teens', 'Youths', 'Ladies', 'Men']
    search_fields = ['date', 'week_of_month']
    list_filter = ['date']

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
