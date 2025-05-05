# ussd_core/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Transactions
from Local_Church.models import USSD_Transactions  # Adjust if your model name differs

@receiver(post_save, sender=Transactions)
def sync_transaction_to_local_church(sender, instance, created, **kwargs):
    if created:
        USSD_Transactions.objects.create(
            Phone_number=instance.Phone_number,
            Txn_code=instance.Txn_code,
            Txn_type=instance.Txn_type,
            Amount=instance.Amount,
            Month=instance.Month,
            Timestamp=instance.Timestamp,
            date=instance.date,
            week_of_month=instance.week_of_month
        )
def sync_transaction_to_local_church(sender, instance, created, **kwargs):
    if created:
        USSD_Transactions.objects.get_or_create(
            Txn_code=instance.Txn_code,
            defaults={
                'Phone_number': instance.Phone_number,
                'Txn_type': instance.Txn_type,
                'Amount': instance.Amount,
                'Month': instance.Month,
                'Timestamp': instance.Timestamp,
            }
        )