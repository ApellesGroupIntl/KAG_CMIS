# from django.db import models
#
# # Create your models here.
# class Transactions (models.Model):
#     Txn_code = models.CharField(max_length=20)
#     Phone_number = models.CharField(max_length=13)
#     Txn_type = models.CharField(max_length=20)
#     Amount = models.DecimalField(max_digits=10, decimal_places=2)
#     Month = models.CharField(max_length=20)
#     Timestamp = models.DateTimeField(auto_now_add=True)
#     church_name = models.CharField(max_length=255, null=True, blank=True, default="Murangá Church")
#
#
#     def __str__(self):
#         return f"{self.Txn_code} - {self.Phone_number} - {self.Txn_type} - {self.Amount} - {self.Month} - {self.Timestamp} - {self.church_name}"
# from django.db import models
#
# # Create your models here.


from django.db import models
from datetime import date
import math


class Transactions(models.Model):
    date = models.DateField(default=date.today)
    week_of_month = models.PositiveIntegerField(blank=True, null=True)
    Txn_code = models.CharField(max_length=20, unique=True)
    Phone_number = models.CharField(max_length=13)
    Txn_type = models.CharField(max_length=20)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    Month = models.CharField(max_length=20)
    Timestamp = models.DateTimeField(auto_now_add=True)
    church_name = models.CharField(max_length=255, null=True, blank=True, default="Murangá Church")
    source = models.CharField(max_length=20, default="section")

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

