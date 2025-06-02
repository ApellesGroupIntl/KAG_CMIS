from django.core.management.base import BaseCommand
from USSD_CORE.models import Transactions
from Local_Church.models import USSD_Transactions
from Section.models import Transactions

class Command(BaseCommand):
    help = "Sync all USSD_CORE transactions to local_church"

    def handle(self, *args, **kwargs):
        count = 0
        for tx in Transactions.objects.all():
            _, created = USSD_Transactions.objects.get_or_create(
                Txn_code=tx.Txn_code,
                defaults={
                    'Phone_number': tx.Phone_number,
                    'Txn_type': tx.Txn_type,
                    'Amount': tx.Amount,
                    'Month': tx.Month,
                    'Timestamp': tx.Timestamp,
                }
            )
            if created:
                count += 1
        self.stdout.write(self.style.SUCCESS(f"{count} transactions synced."))
