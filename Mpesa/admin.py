from django.contrib import admin
from .models import MpesaTransaction

@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'trans_amount', 'trans_id','created_at')
    search_fields = ('phone_number', 'trans_id')
    list_filter = ['created_at']

# Register your models here.
