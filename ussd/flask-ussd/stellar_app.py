from flask import Flask, request
from flask_cors import CORS
import threading
import time
import os
import json
import requests

import africastalking
from dotenv import load_dotenv
from stellar_sdk import (
    Keypair,
    Server,
    TransactionBuilder,
    Network,
)

# --------------------------------------------------
# Load ENV
# --------------------------------------------------
load_dotenv()

app = Flask(__name__)
CORS(app)

# --------------------------------------------------
# Africa's Talking Config
# --------------------------------------------------
USERNAME = os.getenv("AFRICASTALKING_USERNAME")
API_KEY = os.getenv("AFRICASTALKING_API_KEY")
SENDER_ID = os.getenv("AFRICASTALKING_SENDER_ID")
WEB_APP_LINK = os.getenv("WEB_APP_LINK")

if not USERNAME or not API_KEY:
    raise EnvironmentError("Africa's Talking credentials missing")

africastalking.initialize(USERNAME, API_KEY)
sms = africastalking.SMS

# --------------------------------------------------
# Stellar Config (Testnet)
# --------------------------------------------------
HORIZON_URL = os.getenv("HORIZON_URL", "https://horizon-testnet.stellar.org")
STELLAR_SECRET = os.getenv("STELLAR_SECRET_KEY")

if not STELLAR_SECRET:
    raise EnvironmentError("STELLAR_SECRET_KEY missing")

server = Server(HORIZON_URL)
network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE

platform_keypair = Keypair.from_secret(STELLAR_SECRET)
platform_public = platform_keypair.public_key

# --------------------------------------------------
# Phone → Stellar Mapping (local persistence)
# --------------------------------------------------
MAPPING_FILE = "phone_to_stellar.json"

if os.path.exists(MAPPING_FILE):
    with open(MAPPING_FILE, "r") as f:
        phone_to_stellar = json.load(f)
else:
    phone_to_stellar = {}

def save_mapping():
    with open(MAPPING_FILE, "w") as f:
        json.dump(phone_to_stellar, f, indent=2)

# --------------------------------------------------
# SMS Helper
# --------------------------------------------------
def send_sms_with_retries(phone, message, retries=3):
    for attempt in range(retries):
        try:
            sms.send(message=message, recipients=[phone], sender_id=SENDER_ID)
            return
        except Exception as e:
            print(f"[SMS ERROR] {e}")
            time.sleep(2 * (attempt + 1))

# --------------------------------------------------
# Stellar Helpers (CONNECTED VERSION)
# --------------------------------------------------
def generate_account():
    kp = Keypair.random()
    return {"public": kp.public_key, "secret": kp.secret}

def fund_testnet_account(public_key):
    response = requests.get(
        "https://friendbot.stellar.org",
        params={"addr": public_key},
        timeout=10
    )
    response.raise_for_status()

def get_or_create_stellar_account(phone):
    if phone in phone_to_stellar:
        return phone_to_stellar[phone]

    account = generate_account()
    fund_testnet_account(account["public"])

    phone_to_stellar[phone] = account
    save_mapping()

    print(f"[STELLAR] Created account for {phone}: {account['public']}")
    return account

def get_balance(public_key):
    acct = server.accounts().account_id(public_key).call()
    for b in acct["balances"]:
        if b["asset_type"] == "native":
            return float(b["balance"])
    return 0.0

def send_payment(destination, amount):
    source_account = server.load_account(platform_public)

    tx = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=network_passphrase,
            base_fee=100,
        )
        .append_payment_op(destination=destination, amount=str(amount), asset_code="XLM")
        .add_text_memo("KaziChain Payment")
        .set_timeout(30)
        .build()
    )

    tx.sign(platform_keypair)
    server.submit_transaction(tx)

# --------------------------------------------------
# Mock Role Logic
# --------------------------------------------------
def get_user_role(phone):
    return "worker" if phone.endswith("1") else "worker" # Even if it is an "employer"

# --------------------------------------------------
# USSD Endpoint
# --------------------------------------------------
@app.route("/ussd", methods=["POST", "GET"])
def ussd():
    phone = request.values.get("phoneNumber", "")
    text = request.values.get("text", "")
    steps = text.split("*")

    stellar = get_or_create_stellar_account(phone)
    public_key = stellar["public"]

    if text == "":
        return (
            "CON Welcome to KaziChain\n"
            "1. Start with KaziChain\n"
            "2. View Account Details"
        )

    if steps[0] == "1":
        threading.Thread(
            target=send_sms_with_retries,
            args=(phone, f"Welcome to KaziChain: {WEB_APP_LINK}")
        ).start()
        return "END We’ve sent you a link via SMS."

    if steps[0] == "2":
        role = get_user_role(phone)

        if role == "worker":
            if len(steps) == 1:
                return "CON Worker Menu\n1. Withdraw\n2. Balance"

            if steps[1] == "1":
                if len(steps) == 2:
                    return "CON Enter amount (XLM):"
                send_payment(public_key, steps[2])
                return "END Withdrawal sent."

            if steps[1] == "2":
                bal = get_balance(public_key)
                return f"END Your balance is {bal} XLM"

        else:
            if len(steps) == 1:
                return "CON Employer Menu\n1. Balance"

            if steps[1] == "1":
                bal = get_balance(public_key)
                return f"END Your balance is {bal} XLM"

    return "END Invalid option"

# --------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
