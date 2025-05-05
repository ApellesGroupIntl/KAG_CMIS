from .models import Transactions

def save_transaction(session_id, txn_code, phone_number, txn_type, amount, month, timestamp):
    Transactions.objects.create(
        Txn_code=txn_code,
        Phone_number=phone_number,
        Txn_type=txn_type,
        Amount=amount,
        Month=month,
        Timestamp=timestamp,
    )
