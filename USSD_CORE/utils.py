from .models import Transactions
import logging

logger = logging.getLogger(__name__)

def save_transaction(phone_number, txn_type, amount, month, txn_code, timestamp):
    try:
        transaction = Transactions.objects.create(
            Txn_code=txn_code,
            Phone_number=phone_number,
            Txn_type=txn_type,
            Amount=amount,
            Month=month,
            Timestamp=timestamp
        )
        logger.info(f"Transaction saved successfully: {transaction}")
        return transaction
    except Exception as e:
        logger.error(f"Failed to save transaction: {e}", exc_info=True)
        raise
