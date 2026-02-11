from flask import Flask, request
from flask_cors import CORS
import threading
import time
import os
import africastalking  # pip install africastalking
from dotenv import load_dotenv  # pip install python-dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Africa's Talking config from env
USERNAME = os.getenv("AFRICASTALKING_USERNAME")
API_KEY = os.getenv("AFRICASTALKING_API_KEY")
WEB_APP_LINK = os.getenv("WEB_APP_LINK")

if not USERNAME or not API_KEY or not WEB_APP_LINK:
    raise EnvironmentError("AFRICASTALKING_USERNAME, AFRICASTALKING_API_KEY, and WEB_APP_LINK must be set in environment variables")

africastalking.initialize(USERNAME, API_KEY)
sms = africastalking.SMS

def send_sms_with_retries(phone_number, message, retries=3, delay=2):
    attempt = 0
    while attempt < retries:
        try:
            sms.send(message=message, recipients=[phone_number])
            print(f"SMS sent successfully to {phone_number}")
            break
        except Exception as e:
            attempt += 1
            print(f"SMS send attempt {attempt} failed: {e}")
            time.sleep(delay * attempt)
    else:
        print(f"Failed to send SMS to {phone_number} after {retries} attempts.")

@app.route('/ussd', methods=['POST', 'GET'])
def ussd_callback():
    session_id = request.values.get("sessionId", "")
    service_code = request.values.get("serviceCode", "")
    phone_number = request.values.get("phoneNumber", "")
    text = request.values.get("text", "")

    steps = text.split("*")

    # Mock role resolution
    def get_user_role(phone):
        if phone.endswith("1"):
            return "worker"
        return "employer"

    # MAIN MENU
    if text == "":
        response = (
            "CON Welcome to KaziChain\n"
            "1. Start with KaziChain\n"
            "2. View Account Details"
        )
        return response

    # START WITH KAZICHAIN
    if steps[0] == "1":
        message = f"Welcome to KaziChain! Access the web app here: {WEB_APP_LINK}"
        threading.Thread(
            target=send_sms_with_retries, 
            args=(phone_number, message)
        ).start()
        return "END Welcome to KaziChain! We’ve sent you a link via SMS to get started."

    # VIEW ACCOUNT DETAILS
    if steps[0] == "2":
        role = get_user_role(phone_number)

        # Worker Flow
        if role == "worker":
            if len(steps) == 1:
                response = (
                    "CON Account Type: Worker\n"
                    "1. Withdraw Funds\n"
                    "2. Check Account Balance"
                )
                return response
            if steps[1] == "1":
                if len(steps) == 2:
                    return "CON Enter amount to withdraw:"
                amount = steps[2]
                return f"END Withdrawal of KES {amount} successful"
            if steps[1] == "2":
                balance = "KES 5,000"
                return f"END Your balance is {balance}"

        # Employer Flow
        if role == "employer":
            if len(steps) == 1:
                response = (
                    "CON Account Type: Employer\n"
                    "1. View Balance Details\n"
                    "2. Deposit Funds"
                )
                return response
            if steps[1] == "1":
                balance = "KES 12,000"
                return f"END Your balance is {balance}"
            if steps[1] == "2":
                if len(steps) == 2:
                    return "CON Enter amount to deposit:"
                amount = steps[2]
                return f"END Deposit of KES {amount} successful"

    return "END Invalid option"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
