from flask import Flask, request
from flask_cors import CORS
import threading
import time
import os
import json
import requests
import africastalking  # pip install africastalking
from dotenv import load_dotenv  # pip install python-dotenv
from stellar_sdk import Keypair, Server, TransactionBuilder, Network

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Africa's Talking config
USERNAME = os.getenv("AFRICASTALKING_USERNAME")
API_KEY = os.getenv("AFRICASTALKING_API_KEY")
SENDER_ID = os.getenv("AFRICASTALKING_SENDER_ID")
WEB_APP_LINK = os.getenv("WEB_APP_LINK")

if not USERNAME or not API_KEY or not WEB_APP_LINK:
    raise EnvironmentError("AFRICASTALKING_USERNAME, AFRICASTALKING_API_KEY, and WEB_APP_LINK must be set in environment variables")

africastalking.initialize(USERNAME, API_KEY)
sms = africastalking.SMS

# Stellar setup
STELLAR_SECRET = os.getenv("STELLAR_SECRET_KEY")  # Platform escrow account
if not STELLAR_SECRET:
    raise EnvironmentError("STELLAR_SECRET_KEY must be set in environment variables")

server = Server("https://horizon-testnet.stellar.org")
network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE
platform_keypair = Keypair.from_secret(STELLAR_SECRET)
platform_public = platform_keypair.public_key

# Persistent phone -> Stellar mapping
MAPPING_FILE = "phone_to_stellar.json"
if os.path.exists(MAPPING_FILE):
    with open(MAPPING_FILE, "r") as f:
        phone_to_stellar = json.load(f)
else:
    phone_to_stellar = {}

def save_mapping():
    with open(MAPPING_FILE, "w") as f:
        json.dump(phone_to_stellar, f, indent=2)

# SMS helper
def send_sms_with_retries(phone_number, message, retries=3, delay=2):
    attempt = 0
    while attempt < retries:
        try:
            sms.send(message=message, recipients=[phone_number], sender_id=SENDER_ID)
            print(f"[SUCCESS] SMS sent to {phone_number}: {message}")
            break
        except Exception as e:
            attempt += 1
            print(f"[ERROR] SMS send attempt {attempt} for {phone_number} failed: {e}")
            time.sleep(delay * attempt)
    else:
        print(f"[FAILURE] Could not send SMS to {phone_number} after {retries} attempts")

# Stellar helpers
def get_or_create_stellar_account(phone_number):
    """Return Stellar info (public + secret) for a phone, create if new"""
    if phone_number in phone_to_stellar:
        return phone_to_stellar[phone_number]

    # Generate Stellar keypair
    keypair = Keypair.random()
    public_key = keypair.public_key
    secret_key = keypair.secret

    # Fund account on testnet via Friendbot
    response = requests.get(f"https://friendbot.stellar.org?addr={public_key}")
    if response.status_code == 200:
        print(f"[SUCCESS] Funded {phone_number} account with Friendbot: {public_key}")
    else:
        print(f"[ERROR] Friendbot funding failed: {response.text}")

    # Map phone -> Stellar
    phone_to_stellar[phone_number] = {"public": public_key, "secret": secret_key}
    save_mapping()
    print(f"[INFO] Created new Stellar account for {phone_number}: {public_key}")

    return phone_to_stellar[phone_number]

def send_payment(receiver_public, amount):
    """Send XLM from platform escrow to a user"""
    try:
        account = server.load_account(platform_public)
        transaction = (
            TransactionBuilder(
                source_account=account,
                network_passphrase=network_passphrase,
                base_fee=100
            )
            .add_text_memo("KaziChain Payment")
            .append_payment_op(destination=receiver_public, amount=str(amount), asset_code="XLM")
            .set_timeout(30)
            .build()
        )
        transaction.sign(platform_keypair)
        response = server.submit_transaction(transaction)
        print(f"[SUCCESS] Stellar payment submitted: {response}")
        return True
    except Exception as e:
        print(f"[ERROR] Stellar payment failed: {e}")
        return False

def get_balance(public_key):
    """Check XLM balance for a Stellar account"""
    try:
        account = server.accounts().account_id(public_key).call()
        for b in account['balances']:
            if b['asset_type'] == 'native':
                return float(b['balance'])
        return 0.0
    except Exception as e:
        print(f"[ERROR] Could not fetch balance: {e}")
        return 0.0

# Mock role resolution
def get_user_role(phone_number):
    return "worker" if phone_number.endswith("1") else "employer"

# USSD endpoint
@app.route('/ussd', methods=['POST', 'GET'])
def ussd_callback():
    phone_number = request.values.get("phoneNumber", "")
    text = request.values.get("text", "")
    steps = text.split("*")

    # Ensure Stellar account exists dynamically
    stellar_info = get_or_create_stellar_account(phone_number)
    stellar_public = stellar_info["public"]

    # MAIN MENU
    if text == "":
        return (
            "CON Welcome to KaziChain\n"
            "1. Start with KaziChain\n"
            "2. View Account Details"
        )

    # START WITH KAZICHAIN
    if steps[0] == "1":
        message = f"Welcome to KaziChain! Access the web app here: {WEB_APP_LINK}"
        threading.Thread(target=send_sms_with_retries, args=(phone_number, message)).start()
        return "END Welcome to KaziChain! We’ve sent you a link via SMS to get started."

    # VIEW ACCOUNT DETAILS
    if steps[0] == "2":
        role = get_user_role(phone_number)

        # Worker Flow
        if role == "worker":
            if len(steps) == 1:
                return "CON Account Type: Worker\n1. Withdraw Funds\n2. Check Account Balance"

            # Withdraw funds
            if steps[1] == "1":
                if len(steps) == 2:
                    return "CON Enter amount to withdraw (XLM):"
                amount = steps[2]
                success = send_payment(stellar_public, amount)
                msg = f"Your withdrawal of {amount} XLM has been processed successfully." if success else "Withdrawal failed. Try later."
                threading.Thread(target=send_sms_with_retries, args=(phone_number, msg)).start()
                return f"END {msg}"

            # Check balance
            if steps[1] == "2":
                balance = get_balance(stellar_public)
                threading.Thread(target=send_sms_with_retries, args=(phone_number, f"Your balance is {balance} XLM")).start()
                return f"END Your balance is {balance} XLM"

        # Employer Flow
        if role == "employer":
            if len(steps) == 1:
                return "CON Account Type: Employer\n1. View Balance Details\n2. Deposit Funds"

            # View balance
            if steps[1] == "1":
                balance = get_balance(stellar_public)
                threading.Thread(target=send_sms_with_retries, args=(phone_number, f"Your balance is {balance} XLM")).start()
                return f"END Your balance is {balance} XLM"

            # Deposit funds (simulated)
            if steps[1] == "2":
                if len(steps) == 2:
                    return "CON Enter amount to deposit (XLM):"
                amount = steps[2]
                msg = f"Deposit of {amount} XLM recorded. (Simulated for testnet)"
                threading.Thread(target=send_sms_with_retries, args=(phone_number, msg)).start()
                return f"END {msg}"

    return "END Invalid option"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
