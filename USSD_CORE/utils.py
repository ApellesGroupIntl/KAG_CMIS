from USSD_CORE.models import Transactions
import logging
import math

def get_week_of_month(date):
    """
    Returns the week of the month (1-5) starting with Sunday as the first day of the week.
    """
    # Make sure the first day is the 1st of that month
    first_day = date.replace(day=1)

    # Shift weekday so Sunday=0, Monday=1, ..., Saturday=6
    first_day_weekday = (first_day.weekday() + 1) % 7

    dom = date.day
    adjusted_dom = dom + first_day_weekday
    return math.ceil(adjusted_dom / 7)



logger = logging.getLogger(__name__)


def save_local_transaction(phone_number, txn_type, amount, month, txn_code, timestamp, church_name="Murangá Church", source="local"):
    """
    Saves a transaction and lets signals route to either Local_Church or Section app.

    :param source: "local" or "section" to control where to sync
    """
    try:
        transaction = Transactions.objects.create(
            Txn_code=txn_code,
            Phone_number=phone_number,
            Txn_type=txn_type,
            Amount=amount,
            Month=month,
            Timestamp=timestamp,
            date=timestamp.date(),
            week_of_month=get_week_of_month(timestamp.date()),
            church_name=church_name,
            source=source
        )
        logger.info(f"[{source.upper()}] Transaction saved successfully: {transaction}")
        return transaction
    except Exception as e:
        logger.error(f"[{source.upper()}] Failed to save transaction: {e}", exc_info=True)
        raise


def save_section_transaction(phone_number, txn_type, amount, month, txn_code, timestamp, church_name="Murangá Church", source="section"):
    """
    Saves a transaction and lets signals route to either Local_Church or Section app.

    :param source: "local" or "section" to control where to sync
    """
    try:
        transaction = Transactions.objects.create(
            Txn_code=txn_code,
            Phone_number=phone_number,
            Txn_type=txn_type,
            Amount=amount,
            Month=month,
            Timestamp=timestamp,
            date=timestamp.date(),
            week_of_month=get_week_of_month(timestamp.date()),
            church_name=church_name,
            source=source
        )
        logger.info(f"[{source.upper()}] Transaction saved successfully: {transaction}")
        return transaction
    except Exception as e:
        logger.error(f"[{source.upper()}] Failed to save transaction: {e}", exc_info=True)
        raise
