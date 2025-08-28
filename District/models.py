from django.db import models

# Create your models here.
class Transactions (models.Model):
    Txn_code = models.CharField(max_length=20)
    Phone_number = models.CharField(max_length=13)
    Txn_type = models.CharField(max_length=20)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    Month = models.CharField(max_length=20)
    Timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.Txn_code} - {self.Phone_number} - {self.Txn_type} - {self.Amount} - {self.Month} - {self.Timestamp}"
