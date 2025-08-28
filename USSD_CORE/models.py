from django.db import models
from datetime import date
import math

class UssdUser(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    dob = models.DateField()
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone_number})"

class Transactions(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]
    date = models.DateField(default=date.today)
    week_of_month = models.PositiveIntegerField(blank=True, null=True)
    # Txn_code = models.CharField(max_length=20, unique=True)
    Txn_code = models.CharField(max_length=50, unique=True, editable=False)
    Phone_number = models.CharField(max_length=13)
    Txn_type = models.CharField(max_length=20)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    Month = models.CharField(max_length=20)
    Timestamp = models.DateTimeField(auto_now_add=True)
    church_name = models.CharField(max_length=255, null=True, blank=True, default="Murangá Church")
    source = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', blank=True)
    merchant_request_id = models.CharField(max_length=100, blank=True, null=True)
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_receipt_number = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.week_of_month:
            self.week_of_month = self.get_week_of_month(self.date)
        super().save(*args, **kwargs)

    @staticmethod
    def get_week_of_month(d):
        """Calculate the week of the month based on the date."""
        first_day = d.replace(day=1)
        dom = d.day
        adjusted_dom = dom + first_day.weekday()
        return math.ceil(adjusted_dom / 7)

    def __str__(self):
        month_name = self.date.strftime('%B, %Y')  # E.g., April, 2025
        return (
            f"[{month_name} - Week {self.week_of_month}] "
            f"{self.Txn_code} |{self.church_name} | {self.Phone_number} | {self.Txn_type} | "
            f"{self.Amount} | {self.Month} | {self.Timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )

