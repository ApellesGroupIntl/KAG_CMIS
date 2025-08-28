# Local_Church/forms.py
from django import forms
from .models import (
    Cash_Transactions, Mission_Offering, Big_Day, Plot_Buying,
    Attendance, Visitors, Expenses, Missions
)


class ReportFilterForm(forms.Form):
    church = forms.ChoiceField(choices=[], required=False)
    month = forms.ChoiceField(choices=[], required=False)
    year = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate choices dynamically
        self.fields['church'].choices = self.get_church_choices()
        self.fields['month'].choices = self.get_month_choices()
        self.fields['year'].choices = self.get_year_choices()

    def get_church_choices(self):
        # Get unique church names from your database
        from .models import Report
        churches = Report.objects.values_list('church_name', flat=True).distinct()
        return [('', 'All Churches')] + [(church, church) for church in churches]

    def get_month_choices(self):
        months = [
            (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
            (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
            (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
        ]
        return [('', 'All Months')] + months

    def get_year_choices(self):
        # Get unique years from your database
        from .models import Report
        years = Report.objects.values_list('year', flat=True).distinct()
        return [('', 'All Years')] + [(year, year) for year in sorted(years, reverse=True)]

class CashTransactionForm(forms.ModelForm):
    class Meta:
        model = Cash_Transactions
        fields = ['date', 'Tithe', 'Main_Service_Offering', 'Mid_Week_Service_Offering',
                 'Children_Offering', 'Youths_Offering', 'Teens_Offering', 'church_name']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'Tithe': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'Main_Service_Offering': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'Mid_Week_Service_Offering': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'Children_Offering': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'Youths_Offering': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'Teens_Offering': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'church_name': forms.Select(attrs={'class': 'form-control'}),
        }

class MissionOfferingForm(forms.ModelForm):
    class Meta:
        model = Mission_Offering
        fields = ['date', 'Amount', 'church_name']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'Amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'church_name': forms.Select(attrs={'class': 'form-control'}),
        }

class BigDayForm(forms.ModelForm):
    class Meta:
        model = Big_Day
        fields = ['date', 'Big_Day', 'Amount', 'church_name']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'Big_Day': forms.Select(attrs={'class': 'form-control'}),
            'Amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'church_name': forms.Select(attrs={'class': 'form-control'}),
        }

class PlotBuyingForm(forms.ModelForm):
    class Meta:
        model = Plot_Buying
        fields = ['date', 'Amount', 'church_name']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'Amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'church_name': forms.Select(attrs={'class': 'form-control'}),
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['date', 'Men', 'Ladies', 'Youths', 'Teens', 'Children', 'church_name']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'Men': forms.NumberInput(attrs={'class': 'form-control'}),
            'Ladies': forms.NumberInput(attrs={'class': 'form-control'}),
            'Youths': forms.NumberInput(attrs={'class': 'form-control'}),
            'Teens': forms.NumberInput(attrs={'class': 'form-control'}),
            'Children': forms.NumberInput(attrs={'class': 'form-control'}),
            'church_name': forms.Select(attrs={'class': 'form-control'}),
        }

class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitors
        fields = ['date', 'Name', 'Main_Service', 'Mid_Week_Service', 'Phone_number',
                 'Area_of_residence', 'Reason_for_visit', 'Fellowship_again', 'church_name']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'Name': forms.TextInput(attrs={'class': 'form-control'}),
            'Main_Service': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'Mid_Week_Service': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'Phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'Area_of_residence': forms.TextInput(attrs={'class': 'form-control'}),
            'Reason_for_visit': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'Fellowship_again': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'church_name': forms.Select(attrs={'class': 'form-control'}),
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ['date', 'Expense_Name', 'Expense_Amount', 'Expense_Approved', 'church_name']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'Expense_Name': forms.TextInput(attrs={'class': 'form-control'}),
            'Expense_Amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'Expense_Approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'church_name': forms.Select(attrs={'class': 'form-control'}),
        }

class MissionForm(forms.ModelForm):
    class Meta:
        model = Missions
        fields = ['date', 'District_Mission_Contribution', 'KAGDOM_Contribution',
                 'Monthly_Support', 'Missionary_Name', 'church_name']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'District_Mission_Contribution': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'KAGDOM_Contribution': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'Monthly_Support': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'Missionary_Name': forms.TextInput(attrs={'class': 'form-control'}),
            'church_name': forms.Select(attrs={'class': 'form-control'}),
        }