from django.contrib import admin
from .models import Transactions  # or whatever model you created

from .models import Transactions

# admin.site.register(Transactions)

# Register your models here.
class TransactionsAdmin(admin.ModelAdmin):
    list_display = ['date', 'week_of_month', 'Txn_code', 'Phone_number', 'Txn_type', 'Amount', 'Month', 'Timestamp', 'church_name' ]
    search_fields = ['date', 'week_of_month', 'Txn_code', 'Phone_number']
    list_filter = ['date', 'week_of_month']
admin.site.register(Transactions, TransactionsAdmin)


#admin.site.register(Transactions)

