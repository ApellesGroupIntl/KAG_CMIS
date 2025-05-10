from .utils import save_transaction
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from datetime import datetime
from django.utils import timezone
import random
import string

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
            "4. Support Plot Buying\n"
            "5. Big Day Giving\n"
            "0. Exit", content_type="text/plain"
        )

    # OFFERING FLOW
    elif text.startswith("1"):
        if len(user_responses) == 1:
            return HttpResponse("CON Choose Offering Type\n1. Sunday Service\n2. Mid-Week\n00. Back", content_type="text/plain")
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
                try:
                    save_transaction(phone_number, txn_type, amount, current_month, code, timestamp)
                    return HttpResponse(f"END Thank you! You gave Ksh {amount} for {txn_type}. Code: {code}. God bless you!", content_type="text/plain")
                except:
                    return HttpResponse("END Failed to save transaction. Try again.", content_type="text/plain")
            else:
                return HttpResponse("END Transaction cancelled.", content_type="text/plain")

    # TITHE FLOW
    elif text.startswith("2"):
        if len(user_responses) == 1:
            return HttpResponse(f"CON Tithe Payment ({current_month})\nEnter Amount (e.g., 500)\n00. Back", content_type="text/plain")
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
                save_transaction(phone_number, "Tithe", amount, current_month, code, timestamp)
                return HttpResponse(f"END Tithe of Ksh {amount} received. Code: {code}", content_type="text/plain")
            else:
                return HttpResponse("END Transaction cancelled.", content_type="text/plain")

    # MISSION OFFERING FLOW
    elif text.startswith("3"):
        if len(user_responses) == 1:
            return HttpResponse(f"CON Mission Offering ({current_month})\nEnter Amount (e.g., 500)\n00. Back", content_type="text/plain")
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
                save_transaction(phone_number, "Mission Offering", amount, current_month, code, timestamp)
                return HttpResponse(f"END Mission Offering of Ksh {amount} received. Code: {code}", content_type="text/plain")
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
                f"CON Confirm Plot Buying Support\nAmount: Ksh {amount} for {current_month}\n1. Confirm\n2. Cancel\n00. Back",
                content_type="text/plain"
            )
        elif len(user_responses) == 3:
            if user_responses[2] == "1":
                amount = user_responses[1]
                code = generate_transaction_code()
                save_transaction(phone_number, "Plot Buying Support", amount, current_month, code, timestamp)
                return HttpResponse(f"END Thank you! Plot support of Ksh {amount} received. Code: {code}", content_type="text/plain")
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
                save_transaction(phone_number, txn_type, amount, current_month, code, timestamp)
                return HttpResponse(f"END Thank you! Your {txn_type} of Ksh {amount} was received. Code: {code}", content_type="text/plain")
            else:
                return HttpResponse("END Transaction cancelled.", content_type="text/plain")

    # EXIT
    elif text == "0":
        return HttpResponse("END Thank you for using the Church Giving Platform. God bless you!", content_type="text/plain")

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
            "4. Update Attendance\n"
            "5. Big Day Giving\n"
            "0. Exit", content_type="text/plain"
        )

    # OFFERING FLOW
    elif text.startswith("1"):
        if len(user_responses) == 1:
            return HttpResponse("CON Choose Offering Type\n1. Sunday School Service\n2. Main Offering\n00. Back", content_type="text/plain")
        elif len(user_responses) == 2:
            return HttpResponse("CON Enter Amount (e.g., 500)\n00. Back", content_type="text/plain")
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
                try:
                    save_transaction(phone_number, txn_type, amount, current_month, code, timestamp)
                    return HttpResponse(f"END Thank you! You gave Ksh {amount} for {txn_type}. Code: {code}. God bless you!", content_type="text/plain")
                except:
                    return HttpResponse("END Failed to save transaction. Try again.", content_type="text/plain")
            else:
                return HttpResponse("END Transaction cancelled.", content_type="text/plain")

    # TITHE FLOW
    elif text.startswith("2"):
        if len(user_responses) == 1:
            return HttpResponse(f"CON Tithe Payment Update ({current_month})\nEnter Amount (e.g., 500)\n00. Back", content_type="text/plain")
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
                save_transaction(phone_number, "Tithe", amount, current_month, code, timestamp)
                return HttpResponse(f"END Tithe of Ksh {amount} received. Code: {code}", content_type="text/plain")
            else:
                return HttpResponse("END Transaction cancelled.", content_type="text/plain")

    # MISSION OFFERING FLOW
    elif text.startswith("3"):
        if len(user_responses) == 1:
            return HttpResponse(f"CON Update Mission Offering ({current_month})\nEnter Amount (e.g., 500)\n00. Back", content_type="text/plain")
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
                save_transaction(phone_number, "Mission Offering", amount, current_month, code, timestamp)
                return HttpResponse(f"END Mission Offering of Ksh {amount} received. Code: {code}", content_type="text/plain")
            else:
                return HttpResponse("END Transaction cancelled.", content_type="text/plain")

    # ATTENDANCE FLOW
    elif text.startswith("4"):
        if len(user_responses) == 1:
            return HttpResponse("CON Enter Amount for Plot Support (e.g., 500)\n00. Back", content_type="text/plain")
        elif len(user_responses) == 2:
            amount = user_responses[1]
            if not validate_amount(amount):
                return HttpResponse("CON Invalid amount. Enter a number like 500\n00. Back", content_type="text/plain")
            return HttpResponse(
                f"CON Confirm Plot Buying Support\nAmount: Ksh {amount} for {current_month}\n1. Confirm\n2. Cancel\n00. Back",
                content_type="text/plain"
            )
        elif len(user_responses) == 3:
            if user_responses[2] == "1":
                amount = user_responses[1]
                code = generate_section_transaction_code()
                save_transaction(phone_number, "Plot Buying Support", amount, current_month, code, timestamp)
                return HttpResponse(f"END Thank you! Plot support of Ksh {amount} received. Code: {code}", content_type="text/plain")
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
            return HttpResponse("CON Enter Count  (e.g., 25 )\n00. Back", content_type="text/plain")
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
                save_transaction(phone_number, txn_type, amount, current_month, code, timestamp)
                return HttpResponse(f"END Thank you! Your {txn_type} of Count {amount} was received.", content_type="text/plain")
            else:
                return HttpResponse("END Transaction cancelled.", content_type="text/plain")

    # EXIT
    elif text == "0":
        return HttpResponse("END Thank you for using the Section Updates Platform. God bless you!", content_type="text/plain")

    # INVALID INPUT
    return HttpResponse("END Invalid input. Please try again.", content_type="text/plain")
