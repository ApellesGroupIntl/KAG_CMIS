from django.db import models

class MpesaTransaction(models.Model):
    transaction_type = models.CharField(max_length=20)
    trans_id = models.CharField(max_length=20, unique=True)
    trans_time = models.CharField(max_length=20)
    trans_amount = models.DecimalField(max_digits=10, decimal_places=2)
    business_short_code = models.CharField(max_length=10)
    bill_ref_number = models.CharField(max_length=20)
    invoice_number = models.CharField(max_length=20, blank=True, null=True)
    org_account_balance = models.CharField(max_length=20)
    third_party_trans_id = models.CharField(max_length=20)
    msisdn = models.CharField(max_length=13)
    first_name = models.CharField(max_length=50)
    phone_number = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} - {self.trans_amount}"
