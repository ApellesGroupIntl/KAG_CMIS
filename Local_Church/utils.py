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
    try:
        if isinstance(month, str):
            if month.isdigit():
                month = int(month)
            else:
                month = datetime.strptime(month, "%B").month

        start_date = datetime(year, month, 1)
        end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

        logger.info(f"Generating report for {church_name} - {month}/{year}")

        # 1. Attendance
        attendance = Attendance.objects.filter(
            date__gte=start_date,
            date__lt=end_date,
            church_name=church_name
        ).aggregate(
            total_Men=Sum('Men'),
            total_Women=Sum('Ladies'),
            total_Youth=Sum('Youths'),
            total_Teens=Sum('Teens'),
            total_Children=Sum('Children')
        )
        logger.debug(f"Attendance data: {attendance}")

        # 2. USSD Financials
        ussd = USSD_Transactions.objects.filter(
            date__gte=start_date,
            date__lt=end_date,
            church_name=church_name
        ).aggregate(
            Tithes=Sum('Amount', filter=Q(Txn_type='Tithe')),
            Offerings=Sum('Amount', filter=Q(Txn_type='Offering')),
            Missions=Sum('Amount', filter=Q(Txn_type='Mission_Offering'))
        )
        logger.debug(f"USSD data: {ussd}")

        # 3. Cash Financials
        cash = Cash_Transactions.objects.filter(
            date__gte=start_date,
            date__lt=end_date,
            church_name=church_name
        ).aggregate(
            Tithes=Sum('Tithe'),
            Main_Offerings=Sum('Main_Service_Offering'),
            Midweek_Offerings=Sum('Mid_Week_Service_Offering'),
            Youth_Offerings=Sum('Youths_Offering') + Sum('Teens_Offering'),
            Children_Offerings=Sum('Children_Offering')
        )
        logger.debug(f"Cash data: {cash}")

        # 4. Other Offerings
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

        visitors = Visitors.objects.filter(
            date__gte=start_date,
            date__lt=end_date,
            church_name=church_name
        ).count()

        # 5. Create Report
        report = Report.objects.create(
            month=start_date.strftime("%B"),
            year=year,
            church_name=church_name,

            # Attendance
            attendance_Men=attendance.get('total_men') or 0,
            attendance_Women=attendance.get('total_women') or 0,
            attendance_Youth=attendance.get('total_youth') or 0,
            attendance_Teens=attendance.get('total_teens') or 0,
            attendance_Children=attendance.get('total_children') or 0,
            total_Visitors=visitors,

            # Financials
            Tithes=(ussd.get('tithes') or 0) + (cash.get('tithes') or 0),
            Offerings=(ussd.get('offerings') or 0) + (cash.get('main_offerings') or 0) + (cash.get('midweek_offerings') or 0),
            Youth_Offerings=cash.get('youth_offerings') or 0,
            Children_Offerings=cash.get('children_offerings') or 0,
            Missions=(ussd.get('missions') or 0) + mission_offerings,
            other_givings=big_day + plot_buying,
        )

        report.calculate_total_givings()
        logger.info(f"Report created: {report}")
        return report

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise
