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

    # Mock role resolution (replace with DB lookup)
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

    # 1️⃣ START WITH KAZICHAIN
    if steps[0] == "1":
        return (
            "END Welcome to KaziChain!\n"
            "Access the web app here:\n"
            "https://app.kazichain.com"
        )

    # 2️⃣ VIEW ACCOUNT DETAILS → ROLE CHECK
    if steps[0] == "2":
        role = get_user_role(phone_number)

        # WORKER FLOW
        if role == "worker":
            if len(steps) == 1:
                response = (
                    "CON Account Type: Worker\n"
                    "1. Withdraw Funds\n"
                    "2. Check Account Balance"
                )
                return response

            # Withdraw
            if steps[1] == "1":
                if len(steps) == 2:
                    return "CON Enter amount to withdraw:"
                amount = steps[2]
                return f"END Withdrawal of KES {amount} successful"

            # Check Balance
            if steps[1] == "2":
                balance = "KES 5,000"
                return f"END Your balance is {balance}"

        # EMPLOYER FLOW
        if role == "employer":
            if len(steps) == 1:
                response = (
                    "CON Account Type: Employer\n"
                    "1. View Balance Details\n"
                    "2. Deposit Funds"
                )
                return response

            # View Balance
            if steps[1] == "1":
                balance = "KES 12,000"
                return f"END Your balance is {balance}"

            # Deposit
            if steps[1] == "2":
                if len(steps) == 2:
                    return "CON Enter amount to deposit:"
                amount = steps[2]
                return f"END Deposit of KES {amount} successful"

    return "END Invalid option"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
