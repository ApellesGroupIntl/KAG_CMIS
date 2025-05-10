# management/commands/generate_monthly_reports.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from Local_Church.utils import generate_monthly_report
from Local_Church.models import Report


class Command(BaseCommand):
    help = 'Generates monthly reports for all churches'

    def handle(self, *args, **options):
        last_month = timezone.now().month - 1 or 12
        year = timezone.now().year
        if last_month == 12:
            year -= 1

        for church in Report.objects.all():
            try:
                report = generate_monthly_report(church.name, last_month, year)
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully generated report for {church.name} - {report.month} {report.year}"
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Failed to generate report for {church.name}: {str(e)}"
                ))