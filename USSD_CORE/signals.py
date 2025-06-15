from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Transactions
from Local_Church.models import USSD_Transactions
from Section.models import Transactions as SectionTransaction

@receiver(post_save, sender=Transactions)
def sync_transaction(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.source == "local":
        USSD_Transactions.objects.get_or_create(
            Txn_code=instance.Txn_code,
            defaults={
                'Phone_number': instance.Phone_number,
                'Txn_type': instance.Txn_type,
                'Amount': instance.Amount,
                'Month': instance.Month,
                'Timestamp': instance.Timestamp,
                'date': instance.date,
                'week_of_month': instance.week_of_month,
                'church_name': instance.church_name
            }
        )

    elif instance.source == "section":
        SectionTransaction.objects.get_or_create(
            Txn_code=instance.Txn_code,
            defaults={
                'Phone_number': instance.Phone_number,
                'Txn_type': instance.Txn_type,
                'Amount': instance.Amount,
                'Month': instance.Month,
                'Timestamp': instance.Timestamp,
                'date': instance.date,
                'week_of_month': instance.week_of_month,
                'church_name': instance.church_name
            }
        )
