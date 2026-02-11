from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/ussd', methods=['POST', 'GET'])
def ussd_callback():
    session_id = request.values.get("sessionId", "")
    service_code = request.values.get("serviceCode", "")
    phone_number = request.values.get("phoneNumber", "")
    text = request.values.get("text", "")

    steps = text.split("*")

    # STEP 0: PIN ENTRY
    if text == "":
        response = "CON Enter your PIN:"
        return response

    pin = steps[0]

    # Dummy PIN validation (replace with DB check)
    if pin != "1234":
        return "END Invalid PIN"

    # STEP 1: MAIN MENU
    if len(steps) == 1:
        response = "CON Welcome to KaziChain\n"
        response += "1. Start with Us\n"
        response += "2. Account Services"
        return response

    # STEP 2: WALLET SERVICES
    if steps[1] == "1":
        if len(steps) == 2:
            response = "CON Wallet Services\n"
            response += "1. Check Balance\n"
            response += "2. Deposit Funds"
            return response

        # Check Balance
        if steps[2] == "1":
            balance = "KES 10,000"
            return f"END Your balance is {balance}"

        # Deposit Funds
        if steps[2] == "2":
            if len(steps) == 3:
                return "CON Enter amount to deposit:"
            amount = steps[3]
            # process deposit here
            return f"END Deposit of KES {amount} successful"

    # STEP 3: ACCOUNT SERVICES
    if steps[1] == "2":
        if len(steps) == 2:
            response = "CON Account Services\n"
            response += "1. Withdraw Funds\n"
            response += "2. Account Details"
            return response

        # Withdraw Funds
        if steps[2] == "1":
            if len(steps) == 3:
                return "CON Enter amount to withdraw:"
            amount = steps[3]
            # process withdrawal here
            return f"END Withdrawal of KES {amount} successful"

        # Account Details
        if steps[2] == "2":
            balance = "KES 10,000"
            return f"END Account: {phone_number}\nBalance: {balance}"

    return "END Invalid option"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
