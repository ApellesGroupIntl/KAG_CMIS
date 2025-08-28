import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, Q, Count

from .utils import save_section_transaction
from .utils import save_local_transaction
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.utils import timezone
import random
import string
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import datetime
from .models import UssdUser, Transactions
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render
from .mpesa import stk_push_request
from .sms import send_sms_ack
from django.contrib.auth.decorators import login_required


# Add to views.py
@csrf_exempt
def test_callback(request):
    """Test endpoint to verify callback URL is working"""
    return JsonResponse({
        "status": "success",
        "message": "Callback URL is working",
        "received_data": request.body.decode('utf-8') if request.body else "No data"
    })

@csrf_exempt
def mpesa_callback(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        stk_callback = data.get("Body", {}).get("stkCallback", {})
        result_code = stk_callback.get("ResultCode")
        checkout_request_id = stk_callback.get("CheckoutRequestID")

        txn = Transactions.objects.filter(checkout_request_id=checkout_request_id).first()
        if not txn:
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Transaction not found"})

        if result_code == 0:
            # Successful payment
            txn.status = "Success"
            callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
            receipt_number = None
            amount = None

            for item in callback_metadata:
                if item.get("Name") == "MpesaReceiptNumber":
                    receipt_number = item.get("Value")
                elif item.get("Name") == "Amount":
                    amount = item.get("Value")

            txn.mpesa_receipt_number = receipt_number
            txn.save()

            # Send SMS confirmation
            message = f"Payment of Ksh {txn.amount} for {txn.transaction_desc} was successful. Receipt: {receipt_number}"
            send_sms_ack(txn.phone_number, message)

        else:
            # Failed payment
            txn.status = "Failed"
            txn.save()

            # Send SMS failure notification
            message = f"Payment of Ksh {txn.amount} for {txn.transaction_desc} failed. Please try again."
            send_sms_ack(txn.phone_number, message)

        return JsonResponse({"ResultCode": 0, "ResultDesc": "Callback processed successfully"})

    except Exception as e:
        print(f"MPesa callback error: {e}")
        return JsonResponse({"ResultCode": 1, "ResultDesc": "Callback processing failed"})

@login_required
def dashboard(request):
    # Get current date and calculate date ranges
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)

    # Get totals
    total_transactions = Transactions.objects.count()
    total_amount = Transactions.objects.aggregate(Sum('Amount'))['Amount__sum'] or 0

    # Get recent activity
    weekly_transactions = Transactions.objects.filter(date__gte=last_week).count()
    weekly_amount = Transactions.objects.filter(date__gte=last_week).aggregate(Sum('Amount'))['Amount__sum'] or 0

    monthly_transactions = Transactions.objects.filter(date__gte=last_month).count()
    monthly_amount = Transactions.objects.filter(date__gte=last_month).aggregate(Sum('Amount'))['Amount__sum'] or 0

    # Get transaction counts by type (top 5)
    transaction_types = Transactions.objects.values('Txn_type').annotate(
        count=Count('id'),
        total=Sum('Amount')
    ).order_by('-total')[:5]

    context = {
        'total_transactions': total_transactions,
        'total_amount': total_amount,
        'weekly_transactions': weekly_transactions,
        'weekly_amount': weekly_amount,
        'monthly_transactions': monthly_transactions,
        'monthly_amount': monthly_amount,
        'transaction_types': transaction_types,
    }

    return render(request, "dashboard.html", context)


def ussd_home(request):
    return render(request, "USSD_CORE/home.html")


def transaction_list(request):
    # Start with all transactions, ordered by date (newest first)
    transactions_list = Transactions.objects.all().order_by("-date", "-Timestamp")

    # Initialize total amount
    total_amount = 0

    # Get filter parameters from the request
    txn_type_filter = request.GET.get('txn_type')
    source_filter = request.GET.get('source')
    month_filter = request.GET.get('month')  # Format: YYYY-MM

    # Apply filters
    if txn_type_filter:
        transactions_list = transactions_list.filter(Txn_type__icontains=txn_type_filter)

    if source_filter:
        transactions_list = transactions_list.filter(source=source_filter)

    if month_filter:
        # Filter by year and month
        transactions_list = transactions_list.filter(
            Q(date__year=month_filter[:4]) &
            Q(date__month=month_filter[5:7])
        )

    # Calculate total amount for the filtered queryset
    if transactions_list.exists():
        total_amount = transactions_list.aggregate(Sum('Amount'))['Amount__sum'] or 0

    # Pagination - Show 50 transactions per page
    paginator = Paginator(transactions_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'transactions': page_obj,  # Pass the page object instead of the full queryset
        'page_obj': page_obj,  # For pagination controls in template
        'is_paginated': paginator.num_pages > 1,
        'total_amount': total_amount,
    }

    return render(request, "USSD_CORE/transaction_list.html", context)


def transaction_detail(request, pk):
    transaction = get_object_or_404(Transactions, pk=pk)
    return render(request, "USSD_CORE/transaction_detail.html", {"transaction": transaction})


def get_current_month():
    return datetime.now().strftime("%B")


def generate_transaction_code():
    return f"KAG-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"


def validate_amount(amount_str):
    try:
        amount = float(amount_str)
        return amount > 0
    except ValueError:
        return False


def get_transaction_type(menu_level, sub_choice):
    if menu_level == "1":
        return {
            "1": "Sunday Service Offering",
            "2": "Mid-Week Offering"
        }.get(sub_choice, "General Offering")

    elif menu_level == "5":
        return {
            "1": "Men",
            "2": "WWK",
            "3": "Youths",
            "4": "Teens",
            "5": "Children"
        }.get(sub_choice, "Update Attendance")

    elif menu_level == "6":
        return {
            "1": "Men Big Day",
            "2": "WWK Big Day",
            "3": "Youths Big Day",
            "4": "Teens Big Day",
            "5": "Children Big Day",
            "6": "Bishop's Day"
        }.get(sub_choice, "Big Day Giving")
    return ""


@csrf_exempt
def ussd_registration_view(request):
    session_id = request.POST.get("sessionId", "")
    service_code = request.POST.get("serviceCode", "")
    phone_number = request.POST.get("phoneNumber", "")
    text = request.POST.get("text", "")

    inputs = text.split("*") if text else []

    # Step 0 - Welcome message
    if not inputs or inputs[0] == "":
        return JsonResponse({
            "response": "CON Good Morning. This is DMMC Thika.\nIt is time to give and have a blessing time\n1) Register\n2) Proceed without registering"})

    # Step 1 - Register or proceed
    if inputs[0] == "1":
        if len(inputs) == 1:
            return JsonResponse(
                {"response": "CON Read the Terms and Conditions. www.terms.com\n1) I have read and agreed\n2) Decline"})

        if inputs[1] == "1":
            if len(inputs) == 2:
                return JsonResponse({"response": "CON Please enter your full name:"})
            elif len(inputs) == 3:
                return JsonResponse({"response": "CON Enter your Date of Birth (DD/MM/YYYY):"})
            elif len(inputs) == 4:
                name = inputs[2]
                dob = inputs[3]
                return JsonResponse({
                    "response": f"CON Please confirm this details:\nName: {name}\nPhone Number: {phone_number}\nDOB: {dob}\n1) Confirm\n2) Edit"})
            elif len(inputs) == 5:
                if inputs[4] == "1":
                    name = inputs[2]
                    dob_str = inputs[3]
                    try:
                        dob = datetime.strptime(dob_str, "%d/%m/%Y").date()
                        user, created = UssdUser.objects.get_or_create(phone_number=phone_number,
                                                                       defaults={"name": name, "dob": dob})
                        if not created:
                            return JsonResponse({"response": "END You are already registered. Thank you!"})
                        return JsonResponse({
                            "response": f"END Dear {name.upper()}, you have been successfully registered to our DMMC THIKA. Expect a blessing as you give."})
                    except ValueError:
                        return JsonResponse({"response": "END Invalid date format. Please use DD/MM/YYYY."})
                else:
                    return JsonResponse({"response": "END Registration cancelled. You can dial again to try."})

        else:
            return JsonResponse({"response": "END You must agree to the terms to continue."})

    elif inputs[0] == "2":
        return JsonResponse({"response": "END Proceeding without registration. Thank you."})

    return JsonResponse({"response": "END Invalid input. Please dial again."})


@csrf_exempt
def ussd_callback(request):
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    session_id = request.POST.get("sessionId", "")
    phone_number = request.POST.get("phoneNumber", "")
    text = request.POST.get("text", "").strip()
    user_responses = text.split("*") if text else []
    current_month = get_current_month()
    timestamp = timezone.now()

    print(f"Received: {text} => {user_responses}")

    # BACK NAVIGATION
    if user_responses and user_responses[-1] == "00":
        user_responses = user_responses[:-2] if len(user_responses) >= 2 else []
        text = "*".join(user_responses)

    # MAIN MENU
    if text == "":
        return HttpResponse(
            "CON Welcome to KAG MURANGÁ Church Giving Platform\n"
            "1. Give an Offering\n"
            "2. Pay your Tithe\n"
            "3. Mission Offering\n"
            "4. Support Church Expenses\n"
            "5. Big Day Giving\n"
            "0. Exit", content_type="text/plain"
        )

    # OFFERING FLOW
    elif text.startswith("1"):
        if len(user_responses) == 1:
            return HttpResponse("CON Choose Offering Type\n1. Sunday Service\n2. Mid-Week\n00. Back",
                                content_type="text/plain")
        elif len(user_responses) == 2:
            return HttpResponse("CON Enter Amount (e.g., 500)\n00. Back", content_type="text/plain")
        elif len(user_responses) == 3:
            amount = user_responses[2]
            if not validate_amount(amount):
                return HttpResponse("CON Invalid amount. Enter a number like 500\n00. Back", content_type="text/plain")
            txn_type = get_transaction_type("1", user_responses[1])
            code = generate_transaction_code()
            return HttpResponse(
                f"CON Confirm {txn_type}\nAmount: Ksh {amount} for {current_month}\nTransaction Code: {code}\n1. Confirm\n2. Cancel\n00. Back",
                content_type="text/plain"
            )
        elif len(user_responses) == 4:
            if user_responses[3] == "1":
                amount = user_responses[2]
                txn_type = get_transaction_type("1", user_responses[1])
                code = generate_transaction_code()

                # Trigger STK Push
                stk_response = stk_push_request(phone_number, amount, f"{txn_type}-{code}", txn_type)

                if "error" in stk_response:
                    return HttpResponse("END Failed to initiate payment. Please try again.", content_type="text/plain")

                if "ResponseCode" in stk_response and stk_response["ResponseCode"] == "0":
                    # Save transaction with STK details
                    try:
                        transaction = save_local_transaction(
                            phone_number,
                            txn_type,
                            amount,
                            current_month,
                            code,
                            timestamp
                        )
                        # Update with STK details
                        transaction.merchant_request_id = stk_response.get("MerchantRequestID")
                        transaction.checkout_request_id = stk_response.get("CheckoutRequestID")
                        transaction.status = "STK Sent"
                        transaction.save()

                        return HttpResponse("CON Please enter your M-Pesa PIN to complete the payment.",
                                            content_type="text/plain")
                    except:
                        return HttpResponse("END Failed to save transaction. Try again.", content_type="text/plain")
                else:
                    return HttpResponse("END Payment initiation failed. Please try again.", content_type="text/plain")
            else:
                return HttpResponse("END Transaction cancelled.", content_type="text/plain")

    # TITHE FLOW
    elif text.startswith("2"):
        if len(user_responses) == 1:
            return HttpResponse(f"CON Tithe Payment ({current_month})\nEnter Amount (e.g., 500)\n00. Back",
                                content_type="text/plain")
        elif len(user_responses) == 2:
            amount = user_responses[1]
            if not validate_amount(amount):
                return HttpResponse("CON Invalid amount. Enter a number like 500\n00. Back", content_type="text/plain")
            return HttpResponse(
                f"CON Confirm Tithe Payment\nAmount: Ksh {amount} for {current_month}\n1. Confirm\n2. Cancel\n00. Back",
                content_type="text/plain"
            )
        elif len(user_responses) == 3:
            if user_responses[2] == "1":
                amount = user_responses[1]
                code = generate_transaction_code()

                # Trigger STK Push for Tithe
                stk_response = stk_push_request(phone_number, amount, f"Tithe-{code}", "Tithe Payment")

                if "error" in stk_response:
                    return HttpResponse("END Failed to initiate payment. Please try again.", content_type="text/plain")

                if "ResponseCode" in stk_response and stk_response["ResponseCode"] == "0":
                    try:
                        transaction = save_local_transaction(phone_number, "Tithe", amount, current_month, code,
                                                             timestamp)
                        transaction.merchant_request_id = stk_response.get("MerchantRequestID")
                        transaction.checkout_request_id = stk_response.get("CheckoutRequestID")
                        transaction.status = "STK Sent"
                        transaction.save()

                        return HttpResponse("CON Please enter your M-Pesa PIN to complete the payment.",
                                            content_type="text/plain")
                    except:
                        return HttpResponse("END Failed to save transaction. Try again.", content_type="text/plain")
                else:
                    return HttpResponse("END Payment initiation failed. Please try again.", content_type="text/plain")
            else:
                return HttpResponse("END Transaction cancelled.", content_type="text/plain")

    # MISSION OFFERING FLOW
    elif text.startswith("3"):
        if len(user_responses) == 1:
            return HttpResponse(f"CON Mission Offering ({current_month})\nEnter Amount (e.g., 500)\n00. Back",
                                content_type="text/plain")
        elif len(user_responses) == 2:
            amount = user_responses[1]
            if not validate_amount(amount):
                return HttpResponse("CON Invalid amount. Enter a number like 500\n00. Back", content_type="text/plain")
            return HttpResponse(
                f"CON Confirm Mission Offering\nAmount: Ksh {amount} for {current_month}\n1. Confirm\n2. Cancel\n00. Back",
                content_type="text/plain"
            )
        elif len(user_responses) == 3:
            if user_responses[2] == "1":
                amount = user_responses[1]
                code = generate_transaction_code()

                # Trigger STK Push for Mission Offering
                stk_response = stk_push_request(phone_number, amount, f"Mission-{code}", "Mission Offering")

                if "error" in stk_response:
                    return HttpResponse("END Failed to initiate payment. Please try again.", content_type="text/plain")

                if "ResponseCode" in stk_response and stk_response["ResponseCode"] == "0":
                    try:
                        transaction = save_local_transaction(phone_number, "Mission Offering", amount, current_month,
                                                             code, timestamp)
                        transaction.merchant_request_id = stk_response.get("MerchantRequestID")
                        transaction.checkout_request_id = stk_response.get("CheckoutRequestID")
                        transaction.status = "STK Sent"
                        transaction.save()

                        return HttpResponse("CON Please enter your M-Pesa PIN to complete the payment.",
                                            content_type="text/plain")
                    except:
                        return HttpResponse("END Failed to save transaction. Try again.", content_type="text/plain")
                else:
                    return HttpResponse("END Payment initiation failed. Please try again.", content_type="text/plain")
            else:
                return HttpResponse("END Transaction cancelled.", content_type="text/plain")

    # PLOT BUYING SUPPORT
    elif text.startswith("4"):
        if len(user_responses) == 1:
            return HttpResponse("CON Enter Amount for Plot Support (e.g., 500)\n00. Back", content_type="text/plain")
        elif len(user_responses) == 2:
            amount = user_responses[1]
            if not validate_amount(amount):
                return HttpResponse("CON Invalid amount. Enter a number like 500\n00. Back", content_type="text/plain")
            return HttpResponse(
                f"CON Confirm Church Expenses Support\nAmount: Ksh {amount} for {current_month}\n1. Confirm\n2. Cancel\n00. Back",
                content_type="text/plain"
            )
        elif len(user_responses) == 3:
            if user_responses[2] == "1":
                amount = user_responses[1]
                code = generate_transaction_code()

                # Trigger STK Push for Church Expenses
                stk_response = stk_push_request(phone_number, amount, f"Expenses-{code}", "Church Expenses Support")

                if "error" in stk_response:
                    return HttpResponse("END Failed to initiate payment. Please try again.", content_type="text/plain")

                if "ResponseCode" in stk_response and stk_response["ResponseCode"] == "0":
                    try:
                        transaction = save_local_transaction(phone_number, "Church Expenses Support", amount,
                                                             current_month, code, timestamp)
                        transaction.merchant_request_id = stk_response.get("MerchantRequestID")
                        transaction.checkout_request_id = stk_response.get("CheckoutRequestID")
                        transaction.status = "STK Sent"
                        transaction.save()

                        return HttpResponse("CON Please enter your M-Pesa PIN to complete the payment.",
                                            content_type="text/plain")
                    except:
                        return HttpResponse("END Failed to save transaction. Try again.", content_type="text/plain")
                else:
                    return HttpResponse("END Payment initiation failed. Please try again.", content_type="text/plain")
            else:
                return HttpResponse("END Transaction cancelled.", content_type="text/plain")

    # BIG DAY GIVING
    elif text.startswith("5"):
        if len(user_responses) == 1:
            return HttpResponse(
                "CON Select Group for Big Day Giving\n1. Men\n2. WWK\n3. Youths\n4. Teens\n5. Children\n6. Bishop's Day\n00. Back",
                content_type="text/plain"
            )
        elif len(user_responses) == 2:
            return HttpResponse("CON Enter Amount (e.g., 500)\n00. Back", content_type="text/plain")
        elif len(user_responses) == 3:
            amount = user_responses[2]
            if not validate_amount(amount):
                return HttpResponse("CON Invalid amount. Enter number like 500\n00. Back", content_type="text/plain")
            txn_type = get_transaction_type("6", user_responses[1])
            code = generate_transaction_code()
            return HttpResponse(
                f"CON Confirm {txn_type}\nAmount: Ksh {amount}\nTransaction Code: {code}\n1. Confirm\n2. Cancel\n00. Back",
                content_type="text/plain"
            )
        elif len(user_responses) == 4:
            if user_responses[3] == "1":
                txn_type = get_transaction_type("6", user_responses[1])
                amount = user_responses[2]
                code = generate_transaction_code()

                # Trigger STK Push for Big Day Giving
                stk_response = stk_push_request(phone_number, amount, f"{txn_type}-{code}", txn_type)

                if "error" in stk_response:
                    return HttpResponse("END Failed to initiate payment. Please try again.", content_type="text/plain")

                if "ResponseCode" in stk_response and stk_response["ResponseCode"] == "0":
                    try:
                        transaction = save_local_transaction(phone_number, txn_type, amount, current_month, code,
                                                             timestamp)
                        transaction.merchant_request_id = stk_response.get("MerchantRequestID")
                        transaction.checkout_request_id = stk_response.get("CheckoutRequestID")
                        transaction.status = "STK Sent"
                        transaction.save()

                        return HttpResponse("CON Please enter your M-Pesa PIN to complete the payment.",
                                            content_type="text/plain")
                    except:
                        return HttpResponse("END Failed to save transaction. Try again.", content_type="text/plain")
                else:
                    return HttpResponse("END Payment initiation failed. Please try again.", content_type="text/plain")
            else:
                return HttpResponse("END Transaction cancelled.", content_type="text/plain")

    # EXIT
    elif text == "0":
        return HttpResponse("END Thank you for using the Church Giving Platform. God bless you!",
                            content_type="text/plain")

    # INVALID INPUT
    return HttpResponse("END Invalid input. Please try again.", content_type="text/plain")


@csrf_exempt
def ussd_callback_section(request):
    def generate_section_transaction_code():
        return f"KAGSXN-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"

    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    session_id = request.POST.get("sessionId", "")
    phone_number = request.POST.get("phoneNumber", "")
    text = request.POST.get("text", "").strip()
    user_responses = text.split("*") if text else []
    current_month = get_current_month()
    timestamp = timezone.now()

    print(f"Received: {text} => {user_responses}")

    # BACK NAVIGATION
    if user_responses and user_responses[-1] == "00":
        user_responses = user_responses[:-2] if len(user_responses) >= 2 else []
        text = "*".join(user_responses)

    # MAIN MENU
    if text == "":
        return HttpResponse(
            "CON Welcome to KAG MURANGÁ SECTION REPORTING Platform\n"
            "1. Update Offerings\n"
            "2. Update Tithe\n"
            "3. Update Mission Offering\n"
            "4. Update Expenses\n"
            "5. Update Attendance\n"
            "0. Exit", content_type="text/plain"
        )

    # OFFERING FLOW
    elif text.startswith("1"):
        if len(user_responses) == 1:
            return HttpResponse("CON Choose Offering Type\n1. Sunday School Offering\n2. Main Offering\n00. Back",
                                content_type="text/plain")
        elif len(user_responses) == 2:
            return HttpResponse("CON Enter Amount (e.g, 500)\n00. Back", content_type="text/plain")
        elif len(user_responses) == 3:
            amount = user_responses[2]
            if not validate_amount(amount):
                return HttpResponse("CON Invalid amount. Enter a number like 500\n00. Back", content_type="text/plain")
            txn_type = get_transaction_type("1", user_responses[1])
            code = generate_section_transaction_code()
            return HttpResponse(
                f"CON Confirm {txn_type}\nAmount: Ksh {amount} for {current_month}\nTransaction Code: {code}\n1. Confirm\n2. Cancel\n00. Back",
                content_type="text/plain"
            )
        elif len(user_responses) == 4:
            if user_responses[3] == "1":
                amount = user_responses[2]
                txn_type = get_transaction_type("1", user_responses[1])
                code = generate_section_transaction_code()

                # Trigger STK Push for Section Offering
                stk_response = stk_push_request(phone_number, amount, f"{txn_type}-{code}", txn_type)

                if "error" in stk_response:
                    return HttpResponse("END Failed to initiate payment. Please try again.", content_type="text/plain")

                if "ResponseCode" in stk_response and stk_response["ResponseCode"] == "0":
                    try:
                        transaction = save_section_transaction(phone_number, txn_type, amount, current_month, code,
                                                               timestamp)
                        transaction.merchant_request_id = stk_response.get("MerchantRequestID")
                        transaction.checkout_request_id = stk_response.get("CheckoutRequestID")
                        transaction.status = "STK Sent"
                        transaction.save()

                        return HttpResponse("CON Please enter your M-Pesa PIN to complete the payment.",
                                            content_type="text/plain")
                    except:
                        return HttpResponse("END Failed to save transaction. Try again.", content_type="text/plain")
                else:
                    return HttpResponse("END Payment initiation failed. Please try again.", content_type="text/plain")
            else:
                return HttpResponse("END Transaction cancelled.", content_type="text/plain")

    # TITHE FLOW
    elif text.startswith("2"):
        if len(user_responses) == 1:
            return HttpResponse(f"CON Tithe Payment Update ({current_month})\nEnter Amount (e.g., 500)\n00. Back",
                                content_type="text/plain")
        elif len(user_responses) == 2:
            amount = user_responses[1]
            if not validate_amount(amount):
                return HttpResponse("CON Invalid amount. Enter a number like 500\n00. Back", content_type="text/plain")
            return HttpResponse(
                f"CON Confirm Tithe Payment\nAmount: Ksh {amount} for {current_month}\n1. Confirm\n2. Cancel\n00. Back",
                content_type="text/plain"
            )
        elif len(user_responses) == 3:
            if user_responses[2] == "1":
                amount = user_responses[1]
                code = generate_section_transaction_code()

                # Trigger STK Push for Section Tithe
                stk_response = stk_push_request(phone_number, amount, f"Tithe-{code}", "Tithe Payment")

                if "error" in stk_response:
                    return HttpResponse("END Failed to initiate payment. Please try again.", content_type="text/plain")

                if "ResponseCode" in stk_response and stk_response["ResponseCode"] == "0":
                    try:
                        transaction = save_section_transaction(phone_number, "Tithe", amount, current_month, code,
                                                               timestamp)
                        transaction.merchant_request_id = stk_response.get("MerchantRequestID")
                        transaction.checkout_request_id = stk_response.get("CheckoutRequestID")
                        transaction.status = "STK Sent"
                        transaction.save()

                        return HttpResponse("CON Please enter your M-Pesa PIN to complete the payment.",
                                            content_type="text/plain")
                    except:
                        return HttpResponse("END Failed to save transaction. Try again.", content_type="text/plain")
                else:
                    return HttpResponse("END Payment initiation failed. Please try again.", content_type="text/plain")
            else:
                return HttpResponse("END Transaction cancelled.", content_type="text/plain")

    # MISSION OFFERING FLOW
    elif text.startswith("3"):
        if len(user_responses) == 1:
            return HttpResponse(f"CON Update Mission Offering ({current_month})\nEnter Amount (e.g., 500)\n00. Back",
                                content_type="text/plain")
        elif len(user_responses) == 2:
            amount = user_responses[1]
            if not validate_amount(amount):
                return HttpResponse("CON Invalid amount. Enter a number like 500\n00. Back", content_type="text/plain")
            return HttpResponse(
                f"CON Confirm Mission Offering\nAmount: Ksh {amount} for {current_month}\n1. Confirm\n2. Cancel\n00. Back",
                content_type="text/plain"
            )
        elif len(user_responses) == 3:
            if user_responses[2] == "1":
                amount = user_responses[1]
                code = generate_section_transaction_code()

                # Trigger STK Push for Section Mission Offering
                stk_response = stk_push_request(phone_number, amount, f"Mission-{code}", "Mission Offering")

                if "error" in stk_response:
                    return HttpResponse("END Failed to initiate payment. Please try again.", content_type="text/plain")

                if "ResponseCode" in stk_response and stk_response["ResponseCode"] == "0":
                    try:
                        transaction = save_section_transaction(phone_number, "Mission Offering", amount, current_month,
                                                               code, timestamp)
                        transaction.merchant_request_id = stk_response.get("MerchantRequestID")
                        transaction.checkout_request_id = stk_response.get("CheckoutRequestID")
                        transaction.status = "STK Sent"
                        transaction.save()

                        return HttpResponse("CON Please enter your M-Pesa PIN to complete the payment.",
                                            content_type="text/plain")
                    except:
                        return HttpResponse("END Failed to save transaction. Try again.", content_type="text/plain")
                else:
                    return HttpResponse("END Payment initiation failed. Please try again.", content_type="text/plain")
            else:
                return HttpResponse("END Transaction cancelled.", content_type="text/plain")

    # EXPENSES FLOW
    elif text.startswith("4"):
        if len(user_responses) == 1:
            return HttpResponse("CON Enter Amount for Church Expenses (e.g., 500)\n00. Back", content_type="text/plain")
        elif len(user_responses) == 2:
            amount = user_responses[1]
            if not validate_amount(amount):
                return HttpResponse("CON Invalid amount. Enter a number like 500\n00. Back", content_type="text/plain")
            return HttpResponse(
                f"CON Confirm Church Expenses \nAmount: Ksh {amount} for {current_month}\n1. Confirm\n2. Cancel\n00. Back",
                content_type="text/plain"
            )
        elif len(user_responses) == 3:
            if user_responses[2] == "1":
                amount = user_responses[1]
                code = generate_section_transaction_code()

                # Trigger STK Push for Section Expenses
                stk_response = stk_push_request(phone_number, amount, f"Expenses-{code}", "Church Expenses")

                if "error" in stk_response:
                    return HttpResponse("END Failed to initiate payment. Please try again.", content_type="text/plain")

                if "ResponseCode" in stk_response and stk_response["ResponseCode"] == "0":
                    try:
                        transaction = save_section_transaction(phone_number, "Church Expenses", amount, current_month,
                                                               code, timestamp)
                        transaction.merchant_request_id = stk_response.get("MerchantRequestID")
                        transaction.checkout_request_id = stk_response.get("CheckoutRequestID")
                        transaction.status = "STK Sent"
                        transaction.save()

                        return HttpResponse("CON Please enter your M-Pesa PIN to complete the payment.",
                                            content_type="text/plain")
                    except:
                        return HttpResponse("END Failed to save transaction. Try again.", content_type="text/plain")
                else:
                    return HttpResponse("END Payment initiation failed. Please try again.", content_type="text/plain")
            else:
                return HttpResponse("END Transaction cancelled.", content_type="text/plain")

    # ATTENDANCE FLOW
    elif text.startswith("5"):
        if len(user_responses) == 1:
            return HttpResponse(
                "CON Update Attendance\n1. Men\n2. WWK\n3. Youths\n4. Teens\n5. Children\n00. Back",
                content_type="text/plain"
            )
        elif len(user_responses) == 2:
            return HttpResponse("CON Enter Count  (e.g.,25 )\n00. Back", content_type="text/plain")
        elif len(user_responses) == 3:
            amount = user_responses[2]
            if not validate_amount(amount):
                return HttpResponse("CON Invalid count. Enter number like 25\n00. Back", content_type="text/plain")
            txn_type = get_transaction_type("6", user_responses[1])
            code = generate_section_transaction_code()
            return HttpResponse(
                f"CON Confirm {txn_type}\nCount: {amount}\n1. Confirm\n2. Cancel\n00. Back",
                content_type="text/plain"
            )
        elif len(user_responses) == 4:
            if user_responses[3] == "1":
                txn_type = get_transaction_type("6", user_responses[1])
                amount = user_responses[2]
                code = generate_section_transaction_code()
                # For attendance, no STK Push needed
                save_section_transaction(phone_number, txn_type, amount, current_month, code, timestamp)
                return HttpResponse(
                    f"END Thank you! Your update on {txn_type} attendance of Count {amount} was received.",
                    content_type="text/plain")
            else:
                return HttpResponse("END Transaction cancelled.", content_type="text/plain")

    # EXIT
    elif text == "0":
        return HttpResponse("END Thank you for using the Section Updates Platform. God bless you!",
                            content_type="text/plain")

    # INVALID INPUT
    return HttpResponse("END Invalid input. Please try again.", content_type="text/plain")





# import json
#
# from django.core.paginator import Paginator
# from django.db.models import Sum, Q, Count
#
# from .utils import save_section_transaction
# from .utils import save_local_transaction
# from django.views.decorators.csrf import csrf_exempt
# from django.http import HttpResponse
# from datetime import datetime, timedelta
# from django.utils import timezone
# import random
# import string
# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# from datetime import datetime
# from .models import UssdUser, Transactions
# from django.shortcuts import render, get_object_or_404
# from django.shortcuts import render
# # views.py (inside USSD confirmation step)
# from .mpesa import stk_push_request
#
# # def ussd_callback(request):
# #     # after user confirms transaction
# #     if UssdUser:
# #         phone_number = msisdn  # comes from USSD session
# #         amount = entered_amount
# #         account_ref = "USSD-Church"
# #
# #         response = stk_push_request(phone_number, amount, account_ref)
# #
# #         # Save Transaction in DB
# #         Transactions.objects.create(
# #             phone=phone_number,
# #             amount=amount,
# #             txn_type="Offering",
# #             status="Pending",
# #             merchant_request_id=response.get("MerchantRequestID"),
# #             checkout_request_id=response.get("CheckoutRequestID"),
# #         )
# #
# #         return HttpResponse("CON Please enter your M-Pesa PIN to complete the transaction.")
#
# # views.py
# @csrf_exempt
# def mpesa_callback(request):
#     data = json.loads(request.body.decode("utf-8"))
#     result_code = data["Body"]["stkCallback"]["ResultCode"]
#     checkout_request_id = data["Body"]["stkCallback"]["CheckoutRequestID"]
#
#     txn = Transactions.objects.filter(checkout_request_id=checkout_request_id).first()
#     if txn:
#         if result_code == 0:  # success
#             txn.status = "Success"
#         else:
#             txn.status = "Failed"
#         txn.save()
#
#     return JsonResponse({"ResultCode": 0, "ResultDesc": "Callback received successfully"})
#
#
# def dashboard(request):
#     # Get current date and calculate date ranges
#     today = timezone.now().date()
#     last_week = today - timedelta(days=7)
#     last_month = today - timedelta(days=30)
#
#     # Get totals
#     total_transactions = Transactions.objects.count()
#     total_amount = Transactions.objects.aggregate(Sum('Amount'))['Amount__sum'] or 0
#
#     # Get recent activity
#     weekly_transactions = Transactions.objects.filter(date__gte=last_week).count()
#     weekly_amount = Transactions.objects.filter(date__gte=last_week).aggregate(Sum('Amount'))['Amount__sum'] or 0
#
#     monthly_transactions = Transactions.objects.filter(date__gte=last_month).count()
#     monthly_amount = Transactions.objects.filter(date__gte=last_month).aggregate(Sum('Amount'))['Amount__sum'] or 0
#
#     # Get transaction counts by type (top 5)
#     transaction_types = Transactions.objects.values('Txn_type').annotate(
#         count=Count('id'),
#         total=Sum('Amount')
#     ).order_by('-total')[:5]
#
#     context = {
#         'total_transactions': total_transactions,
#         'total_amount': total_amount,
#         'weekly_transactions': weekly_transactions,
#         'weekly_amount': weekly_amount,
#         'monthly_transactions': monthly_transactions,
#         'monthly_amount': monthly_amount,
#         'transaction_types': transaction_types,
#     }
#
#     return render(request, "dashboard.html", context)
# def ussd_home(request):
#     return render(request, "USSD_CORE/home.html")
#
#
# def transaction_list(request):
#     # Start with all transactions, ordered by date (newest first)
#     transactions_list = Transactions.objects.all().order_by("-date", "-Timestamp")
#
#     # Initialize total amount
#     total_amount = 0
#
#     # Get filter parameters from the request
#     txn_type_filter = request.GET.get('txn_type')
#     source_filter = request.GET.get('source')
#     month_filter = request.GET.get('month')  # Format: YYYY-MM
#
#     # Apply filters
#     if txn_type_filter:
#         transactions_list = transactions_list.filter(Txn_type__icontains=txn_type_filter)
#
#     if source_filter:
#         transactions_list = transactions_list.filter(source=source_filter)
#
#     if month_filter:
#         # Filter by year and month
#         transactions_list = transactions_list.filter(
#             Q(date__year=month_filter[:4]) &
#             Q(date__month=month_filter[5:7])
#         )
#
#     # Calculate total amount for the filtered queryset
#     if transactions_list.exists():
#         total_amount = transactions_list.aggregate(Sum('Amount'))['Amount__sum'] or 0
#
#     # Pagination - Show 50 transactions per page
#     paginator = Paginator(transactions_list, 50)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#
#     context = {
#         'transactions': page_obj,  # Pass the page object instead of the full queryset
#         'page_obj': page_obj,  # For pagination controls in template
#         'is_paginated': paginator.num_pages > 1,
#         'total_amount': total_amount,
#     }
#
#     return render(request, "USSD_CORE/transaction_list.html", context)
# def transaction_detail(request, pk):
#     transaction = get_object_or_404(Transactions, pk=pk)
#     return render(request, "USSD_CORE/transaction_detail.html", {"transaction": transaction})
#
# def get_current_month():
#     return datetime.now().strftime("%B")
#
# def generate_transaction_code():
#     return f"KAG-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
#
# def validate_amount(amount_str):
#     try:
#         amount = float(amount_str)
#         return amount > 0
#     except ValueError:
#         return False
#
# def get_transaction_type(menu_level, sub_choice):
#     if menu_level == "1":
#         return {
#             "1": "Sunday Service Offering",
#             "2": "Mid-Week Offering"
#         }.get(sub_choice, "General Offering")
#
#     elif menu_level == "5":
#         return {
#             "1": "Men",
#             "2": "WWK",
#             "3": "Youths",
#             "4": "Teens",
#             "5": "Children"
#         }.get(sub_choice, "Update Attendance")
#
#     elif menu_level == "6":
#         return {
#             "1": "Men Big Day",
#             "2": "WWK Big Day",
#             "3": "Youths Big Day",
#             "4": "Teens Big Day",
#             "5": "Children Big Day",
#             "6": "Bishop's Day"
#         }.get(sub_choice, "Big Day Giving")
#     return ""
#
#
# @csrf_exempt
# def ussd_registration_view(request):
#     session_id = request.POST.get("sessionId", "")
#     service_code = request.POST.get("serviceCode", "")
#     phone_number = request.POST.get("phoneNumber", "")
#     text = request.POST.get("text", "")
#
#     inputs = text.split("*") if text else []
#
#     # Step 0 - Welcome message
#     if not inputs or inputs[0] == "":
#         return JsonResponse({
#                                 "response": "CON Good Morning. This is DMMC Thika.\nIt is time to give and have a blessing time\n1) Register\n2) Proceed without registering"})
#
#     # Step 1 - Register or proceed
#     if inputs[0] == "1":
#         if len(inputs) == 1:
#             return JsonResponse(
#                 {"response": "CON Read the Terms and Conditions. www.terms.com\n1) I have read and agreed\n2) Decline"})
#
#         if inputs[1] == "1":
#             if len(inputs) == 2:
#                 return JsonResponse({"response": "CON Please enter your full name:"})
#             elif len(inputs) == 3:
#                 return JsonResponse({"response": "CON Enter your Date of Birth (DD/MM/YYYY):"})
#             elif len(inputs) == 4:
#                 name = inputs[2]
#                 dob = inputs[3]
#                 return JsonResponse({
#                                         "response": f"CON Please confirm this details:\nName: {name}\nPhone Number: {phone_number}\nDOB: {dob}\n1) Confirm\n2) Edit"})
#             elif len(inputs) == 5:
#                 if inputs[4] == "1":
#                     name = inputs[2]
#                     dob_str = inputs[3]
#                     try:
#                         dob = datetime.strptime(dob_str, "%d/%m/%Y").date()
#                         user, created = UssdUser.objects.get_or_create(phone_number=phone_number,
#                                                                        defaults={"name": name, "dob": dob})
#                         if not created:
#                             return JsonResponse({"response": "END You are already registered. Thank you!"})
#                         return JsonResponse({
#                                                 "response": f"END Dear {name.upper()}, you have been successfully registered to our DMMC THIKA. Expect a blessing as you give."})
#                     except ValueError:
#                         return JsonResponse({"response": "END Invalid date format. Please use DD/MM/YYYY."})
#                 else:
#                     return JsonResponse({"response": "END Registration cancelled. You can dial again to try."})
#
#         else:
#             return JsonResponse({"response": "END You must agree to the terms to continue."})
#
#     elif inputs[0] == "2":
#         return JsonResponse({"response": "END Proceeding without registration. Thank you."})
#
#     return JsonResponse({"response": "END Invalid input. Please dial again."})
#
#
# @csrf_exempt
# def ussd_callback(request):
#     if request.method != "POST":
#         return HttpResponse("Method not allowed", status=405)
#
#     session_id = request.POST.get("sessionId", "")
#     phone_number = request.POST.get("phoneNumber", "")
#     text = request.POST.get("text", "").strip()
#     user_responses = text.split("*") if text else []
#     current_month = get_current_month()
#     timestamp = timezone.now()
#
#     print(f"Received: {text} => {user_responses}")
#
#     # BACK NAVIGATION
#     if user_responses and user_responses[-1] == "00":
#         user_responses = user_responses[:-2] if len(user_responses) >= 2 else []
#         text = "*".join(user_responses)
#
#     # MAIN MENU
#     if text == "":
#         return HttpResponse(
#             "CON Welcome to KAG MURANGÁ Church Giving Platform\n"
#             "1. Give an Offering\n"
#             "2. Pay your Tithe\n"
#             "3. Mission Offering\n"
#             "4. Support Church Expenses\n"
#             "5. Big Day Giving\n"
#             "0. Exit", content_type="text/plain"
#         )
#
#     # OFFERING FLOW
#     elif text.startswith("1"):
#         if len(user_responses) == 1:
#             return HttpResponse("CON Choose Offering Type\n1. Sunday Service\n2. Mid-Week\n00. Back", content_type="text/plain")
#         elif len(user_responses) == 2:
#             return HttpResponse("CON Enter Amount (e.g., 500)\n00. Back", content_type="text/plain")
#         elif len(user_responses) == 3:
#             amount = user_responses[2]
#             if not validate_amount(amount):
#                 return HttpResponse("CON Invalid amount. Enter a number like 500\n00. Back", content_type="text/plain")
#             txn_type = get_transaction_type("1", user_responses[1])
#             code = generate_transaction_code()
#             return HttpResponse(
#                 f"CON Confirm {txn_type}\nAmount: Ksh {amount} for {current_month}\nTransaction Code: {code}\n1. Confirm\n2. Cancel\n00. Back",
#                 content_type="text/plain"
#             )
#         elif len(user_responses) == 4:
#             if user_responses[3] == "1":
#                 amount = user_responses[2]
#                 txn_type = get_transaction_type("1", user_responses[1])
#                 code = generate_transaction_code()
#                 try:
#                     save_local_transaction(phone_number, txn_type, amount, current_month, code, timestamp)
#                     return HttpResponse(f"END Thank you! You gave Ksh {amount} for {txn_type}. Code: {code}. God bless you!", content_type="text/plain")
#                 except:
#                     return HttpResponse("END Failed to save transaction. Try again.", content_type="text/plain")
#             else:
#                 return HttpResponse("END Transaction cancelled.", content_type="text/plain")
#
#     # TITHE FLOW
#     elif text.startswith("2"):
#         if len(user_responses) == 1:
#             return HttpResponse(f"CON Tithe Payment ({current_month})\nEnter Amount (e.g., 500)\n00. Back", content_type="text/plain")
#         elif len(user_responses) == 2:
#             amount = user_responses[1]
#             if not validate_amount(amount):
#                 return HttpResponse("CON Invalid amount. Enter a number like 500\n00. Back", content_type="text/plain")
#             return HttpResponse(
#                 f"CON Confirm Tithe Payment\nAmount: Ksh {amount} for {current_month}\n1. Confirm\n2. Cancel\n00. Back",
#                 content_type="text/plain"
#             )
#         elif len(user_responses) == 3:
#             if user_responses[2] == "1":
#                 amount = user_responses[1]
#                 code = generate_transaction_code()
#                 save_local_transaction(phone_number, "Tithe", amount, current_month, code, timestamp)
#                 return HttpResponse(f"END Tithe of Ksh {amount} received. Code: {code}", content_type="text/plain")
#             else:
#                 return HttpResponse("END Transaction cancelled.", content_type="text/plain")
#
#     # MISSION OFFERING FLOW
#     elif text.startswith("3"):
#         if len(user_responses) == 1:
#             return HttpResponse(f"CON Mission Offering ({current_month})\nEnter Amount (e.g., 500)\n00. Back", content_type="text/plain")
#         elif len(user_responses) == 2:
#             amount = user_responses[1]
#             if not validate_amount(amount):
#                 return HttpResponse("CON Invalid amount. Enter a number like 500\n00. Back", content_type="text/plain")
#             return HttpResponse(
#                 f"CON Confirm Mission Offering\nAmount: Ksh {amount} for {current_month}\n1. Confirm\n2. Cancel\n00. Back",
#                 content_type="text/plain"
#             )
#         elif len(user_responses) == 3:
#             if user_responses[2] == "1":
#                 amount = user_responses[1]
#                 code = generate_transaction_code()
#                 save_local_transaction(phone_number, "Mission Offering", amount, current_month, code, timestamp)
#                 return HttpResponse(f"END Mission Offering of Ksh {amount} received. Code: {code}", content_type="text/plain")
#             else:
#                 return HttpResponse("END Transaction cancelled.", content_type="text/plain")
#
#     # PLOT BUYING SUPPORT
#     elif text.startswith("4"):
#         if len(user_responses) == 1:
#             return HttpResponse("CON Enter Amount for Plot Support (e.g., 500)\n00. Back", content_type="text/plain")
#         elif len(user_responses) == 2:
#             amount = user_responses[1]
#             if not validate_amount(amount):
#                 return HttpResponse("CON Invalid amount. Enter a number like 500\n00. Back", content_type="text/plain")
#             return HttpResponse(
#                 f"CON Confirm Church Expenses Support\nAmount: Ksh {amount} for {current_month}\n1. Confirm\n2. Cancel\n00. Back",
#                 content_type="text/plain"
#             )
#         elif len(user_responses) == 3:
#             if user_responses[2] == "1":
#                 amount = user_responses[1]
#                 code = generate_transaction_code()
#                 save_local_transaction(phone_number, "Church Expenses Support", amount, current_month, code, timestamp)
#                 return HttpResponse(f"END Thank you! Plot support of Ksh {amount} received. Code: {code}", content_type="text/plain")
#             else:
#                 return HttpResponse("END Transaction cancelled.", content_type="text/plain")
#
#     # BIG DAY GIVING
#     elif text.startswith("5"):
#         if len(user_responses) == 1:
#             return HttpResponse(
#                 "CON Select Group for Big Day Giving\n1. Men\n2. WWK\n3. Youths\n4. Teens\n5. Children\n6. Bishop's Day\n00. Back",
#                 content_type="text/plain"
#             )
#         elif len(user_responses) == 2:
#             return HttpResponse("CON Enter Amount (e.g., 500)\n00. Back", content_type="text/plain")
#         elif len(user_responses) == 3:
#             amount = user_responses[2]
#             if not validate_amount(amount):
#                 return HttpResponse("CON Invalid amount. Enter number like 500\n00. Back", content_type="text/plain")
#             txn_type = get_transaction_type("6", user_responses[1])
#             code = generate_transaction_code()
#             return HttpResponse(
#                 f"CON Confirm {txn_type}\nAmount: Ksh {amount}\nTransaction Code: {code}\n1. Confirm\n2. Cancel\n00. Back",
#                 content_type="text/plain"
#             )
#         elif len(user_responses) == 4:
#             if user_responses[3] == "1":
#                 txn_type = get_transaction_type("6", user_responses[1])
#                 amount = user_responses[2]
#                 code = generate_transaction_code()
#                 save_local_transaction(phone_number, txn_type, amount, current_month, code, timestamp)
#                 return HttpResponse(f"END Thank you! Your {txn_type} of Ksh {amount} was received. Code: {code}", content_type="text/plain")
#             else:
#                 return HttpResponse("END Transaction cancelled.", content_type="text/plain")
#
#     # EXIT
#     elif text == "0":
#         return HttpResponse("END Thank you for using the Church Giving Platform. God bless you!", content_type="text/plain")
#
#     # INVALID INPUT
#     return HttpResponse("END Invalid input. Please try again.", content_type="text/plain")
#
# @csrf_exempt
# def ussd_callback_section(request):
#     def generate_section_transaction_code():
#         return f"KAGSXN-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
#
#     if request.method != "POST":
#         return HttpResponse("Method not allowed", status=405)
#
#     session_id = request.POST.get("sessionId", "")
#     phone_number = request.POST.get("phoneNumber", "")
#     text = request.POST.get("text", "").strip()
#     user_responses = text.split("*") if text else []
#     current_month = get_current_month()
#     timestamp = timezone.now()
#
#     print(f"Received: {text} => {user_responses}")
#
#     # BACK NAVIGATION
#     if user_responses and user_responses[-1] == "00":
#         user_responses = user_responses[:-2] if len(user_responses) >= 2 else []
#         text = "*".join(user_responses)
#
#     # MAIN MENU
#     if text == "":
#         return HttpResponse(
#             "CON Welcome to KAG MURANGÁ SECTION REPORTING Platform\n"
#             "1. Update Offerings\n"
#             "2. Update Tithe\n"
#             "3. Update Mission Offering\n"
#             "4. Update Expenses\n"
#             "5. Update Attendance\n"
#             "0. Exit", content_type="text/plain"
#         )
#
#     # OFFERING FLOW
#     elif text.startswith("1"):
#         if len(user_responses) == 1:
#             return HttpResponse("CON Choose Offering Type\n1. Sunday School Offering\n2. Main Offering\n00. Back", content_type="text/plain")
#         elif len(user_responses) == 2:
#             return HttpResponse("CON Enter Amount (e.g, 500)\n00. Back", content_type="text/plain")
#         elif len(user_responses) == 3:
#             amount = user_responses[2]
#             if not validate_amount(amount):
#                 return HttpResponse("CON Invalid amount. Enter a number like 500\n00. Back", content_type="text/plain")
#             txn_type = get_transaction_type("1", user_responses[1])
#             code = generate_section_transaction_code()
#             return HttpResponse(
#                 f"CON Confirm {txn_type}\nAmount: Ksh {amount} for {current_month}\nTransaction Code: {code}\n1. Confirm\n2. Cancel\n00. Back",
#                 content_type="text/plain"
#             )
#         elif len(user_responses) == 4:
#             if user_responses[3] == "1":
#                 amount = user_responses[2]
#                 txn_type = get_transaction_type("1", user_responses[1])
#                 code = generate_section_transaction_code()
#                 try:
#                     save_section_transaction(phone_number, txn_type, amount, current_month, code, timestamp)
#                     return HttpResponse(f"END Thank you! You gave Ksh {amount} for {txn_type}. Code: {code}. God bless you!", content_type="text/plain")
#                 except:
#                     return HttpResponse("END Failed to save transaction. Try again.", content_type="text/plain")
#             else:
#                 return HttpResponse("END Transaction cancelled.", content_type="text/plain")
#
#     # TITHE FLOW
#     elif text.startswith("2"):
#         if len(user_responses) == 1:
#             return HttpResponse(f"CON Tithe Payment Update ({current_month})\nEnter Amount (e.g., 500)\n00. Back", content_type="text/plain")
#         elif len(user_responses) == 2:
#             amount = user_responses[1]
#             if not validate_amount(amount):
#                 return HttpResponse("CON Invalid amount. Enter a number like 500\n00. Back", content_type="text/plain")
#             return HttpResponse(
#                 f"CON Confirm Tithe Payment\nAmount: Ksh {amount} for {current_month}\n1. Confirm\n2. Cancel\n00. Back",
#                 content_type="text/plain"
#             )
#         elif len(user_responses) == 3:
#             if user_responses[2] == "1":
#                 amount = user_responses[1]
#                 code = generate_section_transaction_code()
#                 save_section_transaction(phone_number, "Tithe", amount, current_month, code, timestamp)
#                 return HttpResponse(f"END Tithe of Ksh {amount} received. Code: {code}", content_type="text/plain")
#             else:
#                 return HttpResponse("END Transaction cancelled.", content_type="text/plain")
#
#     # MISSION OFFERING FLOW
#     elif text.startswith("3"):
#         if len(user_responses) == 1:
#             return HttpResponse(f"CON Update Mission Offering ({current_month})\nEnter Amount (e.g., 500)\n00. Back", content_type="text/plain")
#         elif len(user_responses) == 2:
#             amount = user_responses[1]
#             if not validate_amount(amount):
#                 return HttpResponse("CON Invalid amount. Enter a number like 500\n00. Back", content_type="text/plain")
#             return HttpResponse(
#                 f"CON Confirm Mission Offering\nAmount: Ksh {amount} for {current_month}\n1. Confirm\n2. Cancel\n00. Back",
#                 content_type="text/plain"
#             )
#         elif len(user_responses) == 3:
#             if user_responses[2] == "1":
#                 amount = user_responses[1]
#                 code = generate_section_transaction_code()
#                 save_section_transaction(phone_number, "Mission Offering", amount, current_month, code, timestamp)
#                 return HttpResponse(f"END Mission Offering of Ksh {amount} received. Code: {code}", content_type="text/plain")
#             else:
#                 return HttpResponse("END Transaction cancelled.", content_type="text/plain")
#
#     # ATTENDANCE FLOW
#     elif text.startswith("4"):
#         if len(user_responses) == 1:
#             return HttpResponse("CON Enter Amount for Church Expenses (e.g., 500)\n00. Back", content_type="text/plain")
#         elif len(user_responses) == 2:
#             amount = user_responses[1]
#             if not validate_amount(amount):
#                 return HttpResponse("CON Invalid amount. Enter a number like 500\n00. Back", content_type="text/plain")
#             return HttpResponse(
#                 f"CON Confirm Church Expenses \nAmount: Ksh {amount} for {current_month}\n1. Confirm\n2. Cancel\n00. Back",
#                 content_type="text/plain"
#             )
#         elif len(user_responses) == 3:
#             if user_responses[2] == "1":
#                 amount = user_responses[1]
#                 code = generate_section_transaction_code()
#                 save_section_transaction(phone_number, "Church Expenses", amount, current_month, code, timestamp)
#                 return HttpResponse(f"END Thank you! for Updating Expenses of Ksh {amount} received. Code: {code}", content_type="text/plain")
#             else:
#                 return HttpResponse("END Transaction cancelled.", content_type="text/plain")
#
#     # ATTENDANCE FLOW
#     elif text.startswith("5"):
#         if len(user_responses) == 1:
#             return HttpResponse(
#                 "CON Update Attendance\n1. Men\n2. WWK\n3. Youths\n4. Teens\n5. Children\n00. Back",
#                 content_type="text/plain"
#             )
#         elif len(user_responses) == 2:
#             return HttpResponse("CON Enter Count  (e.g.,25 )\n00. Back", content_type="text/plain")
#         elif len(user_responses) == 3:
#             amount = user_responses[2]
#             if not validate_amount(amount):
#                 return HttpResponse("CON Invalid count. Enter number like 25\n00. Back", content_type="text/plain")
#             txn_type = get_transaction_type("6", user_responses[1])
#             code = generate_section_transaction_code()
#             return HttpResponse(
#                 f"CON Confirm {txn_type}\nCount: {amount}\n1. Confirm\n2. Cancel\n00. Back",
#                 content_type="text/plain"
#             )
#         elif len(user_responses) == 4:
#             if user_responses[3] == "1":
#                 txn_type = get_transaction_type("6", user_responses[1])
#                 amount = user_responses[2]
#                 code = generate_section_transaction_code()
#                 save_section_transaction(phone_number, txn_type, amount, current_month, code, timestamp)
#                 return HttpResponse(f"END Thank you! Your update on {txn_type} attendance of Count {amount} was received.", content_type="text/plain")
#             else:
#                 return HttpResponse("END Transaction cancelled.", content_type="text/plain")
#
#     # EXIT
#     elif text == "0":
#         return HttpResponse("END Thank you for using the Section Updates Platform. God bless you!", content_type="text/plain")
#
#     # INVALID INPUT
#     return HttpResponse("END Invalid input. Please try again.", content_type="text/plain")
