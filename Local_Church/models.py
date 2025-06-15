from django.db import models
from datetime import date
from datetime import datetime
from django.utils import timezone
import math

from django.utils.timezone import now
from openpyxl.xml import defusedxml_available


# Create your models here.

class Cash_Transactions(models.Model):
    CHURCH_NAME_CHOICES = [
        ('Murangá Church', 'Murangá Church')
    ]
    church_name = models.CharField(max_length=100, default="unknown", choices=CHURCH_NAME_CHOICES)

    SECTION_NAME_CHOICES = [
        ('Murangá Church', 'Murangá Church')
    ]
    section_name = models.CharField(max_length=100, default="MURANGÁ SECTION")

    DISTRICT_NAME_CHOICES = [
        ('MT. KENYA WEST DISTRICT', 'Murangá Church')
    ]
    district_name = models.CharField(max_length=100, default="MT. KENYA WEST DISTRICT")
    date = models.DateField(default=date.today)
    week_of_month = models.PositiveIntegerField(blank=True, null=True)
    Tithe = models.DecimalField(max_digits=10, decimal_places=2)
    Main_Service_Offering=models.DecimalField(max_digits=10, decimal_places=2)
    Mid_Week_Service_Offering=models.DecimalField(max_digits=10, decimal_places=2)
    Children_Offering=models.DecimalField(max_digits=10, decimal_places=2)
    Youths_Offering=models.DecimalField(max_digits=10, decimal_places=2)
    Teens_Offering=models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Calculate the week of the month before saving
        self.week_of_month = self.get_week_of_month(self.date)
        super().save(*args, **kwargs)

    def get_week_of_month(self, date):
        # Calculate the week of the month
        # Get the first day of the month
        first_day_of_month = date.replace(day=1)

        # Get the day of the month
        day_of_month = date.day

        # Calculate the week number
        week_of_month = math.ceil(day_of_month / 7)
        return week_of_month

    def __str__(self):
        # return f"Date: {self.date}, Week of the Month: {self.week_of_month}"
        month_name = self.date.strftime('%B, %Y')  # E.g., April
        return f"Week of the Month ({month_name}): {self.week_of_month} - {self.Tithe} - {self.Main_Service_Offering} - {self.Mid_Week_Service_Offering} - {self.Children_Offering} - {self.Youths_Offering} - {self.Teens_Offering} "

    # def __str__(self):
    #     return f"{self.Tithe} - {self.Main_Service_Offering} - {self.Mid_Week_Service_Offering} - {self.Children_Offering} - {self.Youths_Offering} - {self.Teens_Offering}"

class Plot_Buying(models.Model):
    date = models.DateField(default=date.today)
    CHURCH_NAME_CHOICES = [
        ('Murangá Church', 'Murangá Church')
    ]
    church_name = models.CharField(max_length=100,default="Unknown", choices=CHURCH_NAME_CHOICES)

    SECTION_NAME_CHOICES = [
        ('Murangá Church', 'Murangá Church')
    ]
    section_name = models.CharField(max_length=100, default="MURANGÁ SECTION")

    DISTRICT_NAME_CHOICES = [
        ('MT. KENYA WEST DISTRICT', 'Murangá Church')
    ]
    district_name = models.CharField(max_length=100, default="MT. KENYA WEST DISTRICT")
    Amount = models.DecimalField(max_digits=10, decimal_places=2)




    def __str__(self):
        # return f"Date: {self.date}, Week of the Month: {self.week_of_month}"
        month_name = self.date.strftime('%B')  # E.g., April
        return f"{month_name} - {self.Amount} "

    # def __str__(self):
    #     return f"{self.Tithe} - {self.Main_Service_Offering} - {self.Mid_Week_Service_Offering} - {self.Children_Offering} - {self.Youths_Offering} - {self.Teens_Offering}"

class Mission_Offering(models.Model):
    date = models.DateField(default=date.today)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)


    CHURCH_NAME_CHOICES = [
        ('Murangá Church', 'Murangá Church')
    ]
    church_name = models.CharField(max_length=100, default="unknown",choices=CHURCH_NAME_CHOICES)

    SECTION_NAME_CHOICES = [
        ('Murangá Church', 'Murangá Church')
    ]
    section_name = models.CharField(max_length=100, default="MURANGÁ SECTION")

    DISTRICT_NAME_CHOICES = [
        ('MT. KENYA WEST DISTRICT', 'Murangá Church')
    ]
    district_name = models.CharField(max_length=100, default="MT. KENYA WEST DISTRICT")
    def __str__(self):
        # return f"Date: {self.date}, Week of the Month: {self.week_of_month}"
        month_name = self.date.strftime('%B')  # E.g., April
        return f"{month_name} -{self.Amount} "

    # def __str__(self):
    #     return f"{self.Tithe} - {self.Main_Service_Offering} - {self.Mid_Week_Service_Offering} - {self.Children_Offering} - {self.Youths_Offering} - {self.Teens_Offering}"

class Missions(models.Model):
    date = models.DateField(default=date.today)
    District_Mission_Contribution =models.DecimalField(max_digits=10, decimal_places=2)
    KAGDOM_Contribution = models.DecimalField(null=True,max_digits=10, decimal_places=2)
    Monthly_Support =models.DecimalField(max_digits=10, decimal_places=2)
    Missionary_Name = models.CharField(max_length=50, default="Name")
    Total_amount = models.DecimalField(max_digits=12,decimal_places=2)

    CHURCH_NAME_CHOICES = [
        ('Murangá Church', 'Murangá Church')
    ]
    church_name = models.CharField(max_length=100, default="unknown",choices=CHURCH_NAME_CHOICES)

    SECTION_NAME_CHOICES = [
        ('Murangá Church', 'Murangá Church')
    ]
    section_name = models.CharField(max_length=100, default="MURANGÁ SECTION")

    DISTRICT_NAME_CHOICES = [
        ('MT. KENYA WEST DISTRICT', 'Murangá Church')
    ]
    district_name = models.CharField(max_length=100, default="MT. KENYA WEST DISTRICT")
    def __str__(self):
        # return f"Date: {self.date}, Week of the Month: {self.week_of_month}"
        month_name = self.date.strftime('%B')  # E.g., April
        return f"{month_name} -{self.KAGDOM_Contribution} -{self.District_Mission_Contribution} -{self.Missionary_Name} -{self.Total_amount} - {self.Monthly_Support} "

    # def __str__(self):
    #     return f"{self.Tithe} - {self.Main_Service_Offering} - {self.Mid_Week_Service_Offering} - {self.Children_Offering} - {self.Youths_Offering} - {self.Teens_Offering}"


class Big_Day(models.Model):
    BIG_DAY_CHOICES = [
        ('Men Day','Men Day'),
        ('WWK Day','WWK Day'),
        ('Youths Day', 'Youths Day'),
        ('Teens Day', 'Teens Day'),
        ('Childrens Day', 'Childrens Day')
    ]
    Big_Day= models.CharField(max_length=50, default="unknown",choices=BIG_DAY_CHOICES)
    date = models.DateField(default=date.today)
    week_of_month = models.PositiveIntegerField(blank=True, null=True)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    CHURCH_NAME_CHOICES = [
        ('Murangá Church', 'Murangá Church')
    ]
    church_name = models.CharField(max_length=100, default="unknown",choices=CHURCH_NAME_CHOICES)

    SECTION_NAME_CHOICES = [
        ('Murangá Church', 'Murangá Church')
    ]
    section_name = models.CharField(max_length=100, default="MURANGÁ SECTION")

    DISTRICT_NAME_CHOICES = [
        ('MT. KENYA WEST DISTRICT', 'Murangá Church')
    ]
    district_name = models.CharField(max_length=100, default="MT. KENYA WEST DISTRICT")


    def __str__(self):
        # return f"Date: {self.date}, Week of the Month: {self.week_of_month}"
        month_name = self.date.strftime('%B')  # E.g., April
        return f"{month_name} -{self.Amount} "

    # def __str__(self):
    #     return f"{self.Tithe} - {self.Main_Service_Offering} - {self.Mid_Week_Service_Offering} - {self.Children_Offering} - {self.Youths_Offering} - {self.Teens_Offering}"


class USSD_Transactions (models.Model):
    date = models.DateField(default=date.today)
    week_of_month = models.PositiveIntegerField(blank=True, null=True)
    Txn_code = models.CharField(max_length=20)
    Phone_number = models.CharField(max_length=13)
    Txn_type = models.CharField(max_length=20)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    Month = models.CharField(max_length=20)
    Timestamp = models.DateTimeField(auto_now_add=True)
    CHURCH_NAME_CHOICES = [
        ('Murangá Church', 'Murangá Church')
    ]
    church_name = models.CharField(max_length=100, choices=CHURCH_NAME_CHOICES)

    SECTION_NAME_CHOICES = [
        ('Murangá Church', 'Murangá Church')
    ]
    section_name = models.CharField(max_length=100, default="MURANGÁ SECTION")

    DISTRICT_NAME_CHOICES = [
        ('MT. KENYA WEST DISTRICT', 'Murangá Church')
    ]
    district_name = models.CharField(max_length=100, default="MT. KENYA WEST DISTRICT")
    source = models.CharField(max_length=20, default="local")

    def save(self, *args, **kwargs):
        # Calculate the week of the month before saving
        self.week_of_month = self.get_week_of_month(self.date)
        super().save(*args, **kwargs)

    def get_week_of_month(self, date):
        # Calculate the week of the month
        # Get the first day of the month
        first_day_of_month = date.replace(day=1)

        # Get the day of the month
        day_of_month = date.day

        # Calculate the week number
        week_of_month = math.ceil(day_of_month / 7)
        return week_of_month

    def __str__(self):
        # return f"Date: {self.date}, Week of the Month: {self.week_of_month}"
        month_name = self.date.strftime('%B, %Y')  # E.g., April
        return f"Week of the Month ({month_name}): {self.week_of_month} -{self.Txn_code} - {self.Phone_number} - {self.Txn_type} - {self.Amount} - {self.Month} - {self.Timestamp}"

    # def __str__(self):
    #     return f"{self.Txn_code} - {self.Phone_number} - {self.Txn_type} - {self.Amount} - {self.Month} - {self.Timestamp}"

class Attendance (models.Model):
      date = models.DateField(default=date.today)
      week_of_month = models.PositiveIntegerField(blank=True, null=True)
      Ladies = models.IntegerField(default=0)
      Men = models.IntegerField(default=0)
      Youths = models.IntegerField(default=0)
      Teens = models.IntegerField(default=0)
      Children = models.IntegerField(default=0)

      CHURCH_NAME_CHOICES = [
          ('Murangá Church', 'Murangá Church')
      ]
      church_name = models.CharField(max_length=100, default="unknown",choices=CHURCH_NAME_CHOICES)

      SECTION_NAME_CHOICES = [
          ('Murangá Church', 'Murangá Church')
      ]
      section_name = models.CharField(max_length=100, default="MURANGÁ SECTION")

      DISTRICT_NAME_CHOICES = [
          ('MT. KENYA WEST DISTRICT', 'Murangá Church')
      ]
      district_name = models.CharField(max_length=100, default="MT. KENYA WEST DISTRICT")

      def save(self, *args, **kwargs):
          # Calculate the week of the month before saving
          self.week_of_month = self.get_week_of_month(self.date)
          super().save(*args, **kwargs)

      def get_week_of_month(self, date):
         # Calculate the week of the month
         # Get the first day of the month
         first_day_of_month = date.replace(day=1)

         # Get the day of the month
         day_of_month = date.day

         # Calculate the week number
         week_of_month = math.ceil(day_of_month / 7)
         return week_of_month

      def __str__(self):
         #return f"Date: {self.date}, Week of the Month: {self.week_of_month}"
         month_name = self.date.strftime('%B, %Y')  # E.g., April
         return f"Week of the Month ({month_name}): {self.week_of_month}, Ladies, Men, Youths, Teens Children"

class Visitors(models.Model):
    date = models.DateField(default=date.today)
    week_of_month = models.PositiveIntegerField(blank=True, null=True)
    Name = models.CharField(max_length=50)
    Main_Service = models.BooleanField()
    Mid_Week_Service = models.BooleanField()
    Phone_number = models.CharField(max_length=13)
    Area_of_residence = models.CharField(max_length=100)
    Reason_for_visit = models.CharField(max_length=100, blank=True, null=True)
    Fellowship_again = models.BooleanField()
    CHURCH_NAME_CHOICES = [
        ('Murangá Church', 'Murangá Church')
    ]
    church_name = models.CharField(max_length=100, default="unknown", choices=CHURCH_NAME_CHOICES)

    SECTION_NAME_CHOICES = [
        ('Murangá Church', 'Murangá Church')
    ]
    section_name = models.CharField(max_length=100, default="MURANGÁ SECTION")

    DISTRICT_NAME_CHOICES = [
        ('MT. KENYA WEST DISTRICT', 'Murangá Church')
    ]
    district_name = models.CharField(max_length=100, default="MT. KENYA WEST DISTRICT")

    def save(self, *args, **kwargs):
        # Automatically calculate week of month
        self.week_of_month = self.get_week_of_month(self.date)
        super().save(*args, **kwargs)

    def get_week_of_month(self, date_obj):
        # Get first day of the month and calculate the week
        first_day_of_month = date_obj.replace(day=1)
        adjusted_dom = date_obj.day + first_day_of_month.weekday()
        return int(math.ceil(adjusted_dom / 7.0))

    def __str__(self):
        month_name = self.date.strftime('%B, %Y')
        return (
            f"Week ({month_name}) {self.week_of_month}: "
            f"{self.Name} | Main: {self.Main_Service} | Mid: {self.Mid_Week_Service} | "
            f"{self.Phone_number} | {self.Area_of_residence} | Again: {self.Fellowship_again}"
        )

    class Meta:
        ordering = ['-date']
        # permissions = [
        #     ("can_add_visitors", "Can add visitors"),
        #     ("can_change_visitors", "Can change visitors"),
        #     ("can_delete_visitors", "Can delete visitors"),
        #     ("can_view_visitors", "Can view visitors"),
        # ]

class Expenses(models.Model):
    CHURCH_NAME_CHOICES = [
        ('Murangá Church', 'Murangá Church')
    ]
    church_name = models.CharField(max_length=100, default="unknown", choices=CHURCH_NAME_CHOICES)

    SECTION_NAME_CHOICES = [
        ('Murangá Church', 'Murangá Church')
    ]
    section_name = models.CharField(max_length=100, default="MURANGÁ SECTION")

    DISTRICT_NAME_CHOICES = [
        ('MT. KENYA WEST DISTRICT', 'Murangá Church')
    ]
    district_name = models.CharField(max_length=100, default="MT. KENYA WEST DISTRICT")
    date = models.DateField(default=date.today)
    week_of_month = models.PositiveIntegerField(blank=True, null=True)
    Expense_Name =models.CharField(max_length=100)
    Expense_Amount = models.DecimalField(max_digits=6, decimal_places=2)
    Expense_Approved = models.BooleanField()
    #generated_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate the week of the month before saving
        self.week_of_month = self.get_week_of_month(self.date)
        super().save(*args, **kwargs)

    def get_week_of_month(self, date):
        # Calculate the week of the month
        # Get the first day of the month
        first_day_of_month = date.replace(day=1)

        # Get the day of the month
        day_of_month = date.day

        # Calculate the week number
        week_of_month = math.ceil(day_of_month / 7)
        return week_of_month



    def __str__(self):
         month_name = self.date.strftime('%B, %Y')
         return f"Week of the Month ({month_name}): {self.week_of_month} {self.Expense_Name} ({self.Expense_Amount}) "

class Report(models.Model):
    MONTH_CHOICES = [
        ('January', 'January'), ('February', 'February'), ('March', 'March'),
        ('April', 'April'), ('May', 'May'), ('June', 'June'),
        ('July', 'July'), ('August', 'August'), ('September', 'September'),
        ('October', 'October'), ('November', 'November'), ('December', 'December')
    ]

    CHURCH_NAME_CHOICES = [
        ('Murangá Church', 'Murangá Church')
    ]

    SECTION_NAME_CHOICES = [
        ('Murangá Church', 'Murangá Church')
    ]

    DISTRICT_NAME_CHOICES = [
        ('MT. KENYA WEST DISTRICT', 'Murangá Church')
    ]

    APPROVIE_NAME_CHOICES = [
        ('Bishop Ben Irungu', 'Bishop Ben Irungu')
    ]

    # Basic Info
    month = models.CharField(max_length=20, choices=MONTH_CHOICES)
    year = models.PositiveIntegerField(default=datetime.now().year)
    church_name = models.CharField(max_length=100, choices=CHURCH_NAME_CHOICES, default="unknown")
    section_name = models.CharField(max_length=100, choices=SECTION_NAME_CHOICES, default="MURANGÁ SECTION")
    district_name = models.CharField(max_length=100, choices=DISTRICT_NAME_CHOICES, default="MT. KENYA WEST DISTRICT")

    # Attendance
    attendance_Men = models.PositiveIntegerField(default=0)
    attendance_Women = models.PositiveIntegerField(default=0)
    attendance_Youth = models.PositiveIntegerField(default=0)
    attendance_Teens = models.PositiveIntegerField(default=0)
    attendance_Children = models.PositiveIntegerField(default=0)
    total_Visitors = models.PositiveIntegerField(default=0)

    # Financials
    Tithes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Offerings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Youth_Offerings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Children_Offerings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Missions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_givings = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    total_givings = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Meta Info
    is_approved = models.BooleanField(default=False)
    approved_by = models.CharField(max_length=100, choices=APPROVIE_NAME_CHOICES, null=True, default="Bishop Ben Irungu")
    notes = models.TextField(blank=True, null=True)
    generated_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('month', 'year', 'church_name')
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.church_name} - {self.month} {self.year} Report"

    def calculate_total_givings(self):
        self.total_givings = (
            self.Tithes +
            self.Offerings +
            self.Youth_Offerings +
            self.Children_Offerings +
            self.Missions +
            self.other_givings
        )
        self.save()

    def get_attendance_total(self):
        return (
            self.attendance_Men +
            self.attendance_Women +
            self.attendance_Youth +
            self.attendance_Teens +
            self.attendance_Children
        )