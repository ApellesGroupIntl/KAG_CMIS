from datetime import datetime
from django.db.models import Sum, Q
from .models import (
    Attendance,
    USSD_Transactions,
    Cash_Transactions,
    Mission_Offering,
    Big_Day,
    Plot_Buying,
    Report,
    Visitors
)
import logging

logger = logging.getLogger(__name__)


def generate_monthly_report(church_name, month, year):
    """
    Generates a comprehensive monthly report by aggregating data from multiple models
    """
    try:
        # Convert month name to number if needed
        if isinstance(month, str):
            month = datetime.strptime(month, "%B").month

        # Create date range
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        logger.info(f"Generating report for {church_name} - {month}/{year}")

        # 1. Get Attendance Data
        attendance = Attendance.objects.filter(
            date__gte=start_date,
            date__lt=end_date,
            church_name=church_name
        ).aggregate(
            total_men=Sum('Men'),
            total_women=Sum('Ladies'),
            total_youth=Sum('Youths'),
            total_children=Sum('Children'),
            total_teens=Sum('Teens')
        )
        logger.debug(f"Attendance data: {attendance}")

        # 2. Get Financial Data
        # USSD Transactions
        ussd = USSD_Transactions.objects.filter(
            date__gte=start_date,
            date__lt=end_date,
            church_name=church_name
        ).aggregate(
            tithes=Sum('Amount', filter=Q(Txn_type='tithe')),
            offerings=Sum('Amount', filter=Q(Txn_type='offering')),
            missions=Sum('Amount', filter=Q(Txn_type='mission_offering'))
        )
        logger.debug(f"USSD data: {ussd}")

        # Cash Transactions
        cash = Cash_Transactions.objects.filter(
            date__gte=start_date,
            date__lt=end_date,
            church_name=church_name
        ).aggregate(
            tithes=Sum('Tithe'),
            main_offerings=Sum('Main_Service_Offering'),
            midweek_offerings=Sum('Mid_Week_Service_Offering'),
            youth_offerings=Sum('Youths_Offering') + Sum('Teens_Offering'),
            children_offerings=Sum('Children_Offering')
        )
        logger.debug(f"Cash data: {cash}")

        # Other financial data
        mission_offerings = Mission_Offering.objects.filter(
            date__gte=start_date,
            date__lt=end_date,
            church_name=church_name
        ).aggregate(total=Sum('Amount'))['total'] or 0

        big_day = Big_Day.objects.filter(
            date__gte=start_date,
            date__lt=end_date,
            church_name=church_name
        ).aggregate(total=Sum('Amount'))['total'] or 0

        plot_buying = Plot_Buying.objects.filter(
            date__gte=start_date,
            date__lt=end_date,
            church_name=church_name
        ).aggregate(total=Sum('Amount'))['total'] or 0

        # Visitors
        visitors = Visitors.objects.filter(
            date__gte=start_date,
            date__lt=end_date,
            church_name=church_name
        ).count()

        # Create the report
        report = Report.objects.create(
            month=start_date.strftime("%B"),
            year=year,
            church_name=church_name,

            # Attendance
            attendance_men=attendance.get('total_men', 0) or 0,
            attendance_women=attendance.get('total_women', 0) or 0,
            attendance_youth=attendance.get('total_youth', 0) or 0,
            attendance_children=attendance.get('total_children', 0) or 0,
            attendance_teens=attendance.get('total_teens', 0) or 0,
            total_visitors=visitors,

            # Financials
            tithes=(ussd.get('tithes', 0) or 0) + (cash.get('tithes', 0) or 0),
            offerings=(ussd.get('offerings', 0) or 0) + (cash.get('main_offerings', 0) or 0) + (
                        cash.get('midweek_offerings', 0) or 0),
            youth_offerings=cash.get('youth_offerings', 0) or 0,
            children_offerings=cash.get('children_offerings', 0) or 0,
            missions=(ussd.get('missions', 0) or 0) + mission_offerings,
            other_givings=big_day + plot_buying,
        )

        report.calculate_total_givings()
        logger.info(f"Report created: {report}")
        return report

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise