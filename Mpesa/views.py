from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .stk_push import lipa_na_mpesa_online
from .models import MpesaTransaction
from datetime import datetime

@csrf_exempt
def initiate_payment(request):
    data = json.loads(request.body)
    phone = data.get("phone")
    amount = data.get("amount")

    response = lipa_na_mpesa_online(phone, amount)

    MpesaTransaction.objects.create(
        phone_number=phone,
        amount=amount,
        checkout_request_id=response.get("CheckoutRequestID"),
        merchant_request_id=response.get("MerchantRequestID"),
        status="Pending"
    )

    return JsonResponse({"message": "STK Push Sent", "response": response})

@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body)
    try:
        result = data['Body']['stkCallback']
        metadata = {item['Name']: item.get('Value') for item in result.get('CallbackMetadata', {}).get('Item', [])}

        txn = MpesaTransaction.objects.filter(checkout_request_id=result['CheckoutRequestID']).first()
        if txn:
            txn.result_code = result['ResultCode']
            txn.result_desc = result['ResultDesc']
            txn.receipt_number = metadata.get('MpesaReceiptNumber')
            txn.amount = metadata.get('Amount')
            txn.phone_number = metadata.get('PhoneNumber')
            txn.transaction_date = datetime.strptime(str(metadata.get('TransactionDate')), "%Y%m%d%H%M%S") if metadata.get('TransactionDate') else None
            txn.status = "Success" if result['ResultCode'] == 0 else "Failed"
            txn.save()

    except Exception as e:
        print("Callback error:", e)

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

@csrf_exempt
def mpesa_validation(request):
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

@csrf_exempt
def mpesa_confirmation(request):
    data = json.loads(request.body)
    MpesaTransaction.objects.create(
        transaction_type=data['TransactionType'],
        trans_id=data['TransID'],
        trans_time=data['TransTime'],
        trans_amount=data['TransAmount'],
        business_short_code=data['BusinessShortCode'],
        bill_ref_number=data['BillRefNumber'],
        invoice_number=data.get('InvoiceNumber'),
        org_account_balance=data.get('OrgAccountBalance'),
        third_party_trans_id=data.get('ThirdPartyTransID'),
        msisdn=data['MSISDN'],
        first_name=data.get('FirstName')
    )
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Received Successfully"})
