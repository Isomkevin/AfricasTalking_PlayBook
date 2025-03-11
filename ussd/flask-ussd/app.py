from flask import Flask, request, session
import os
import sqlite3
import datetime
import hashlib
import random
import string
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'ussd_secret_key'  # For session management
CORS(app)

# Database setup
def init_db():
    conn = sqlite3.connect('ussd_database.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        phone_number TEXT PRIMARY KEY,
        pin TEXT NOT NULL,
        account_number TEXT NOT NULL,
        balance REAL DEFAULT 0.0,
        name TEXT,
        language TEXT DEFAULT 'English'
    )
    ''')
    
    # Transactions table
    c.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone_number TEXT,
        transaction_type TEXT,
        amount REAL,
        recipient TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (phone_number) REFERENCES users (phone_number)
    )
    ''')
    
    # Insert demo user if not exists
    c.execute("SELECT * FROM users WHERE phone_number = '+254700000000'")
    if not c.fetchone():
        # Store PIN as hashed value (using simple hash for demo)
        hashed_pin = hashlib.sha256('1234'.encode()).hexdigest()
        c.execute("INSERT INTO users (phone_number, pin, account_number, balance, name) VALUES (?, ?, ?, ?, ?)", 
                 ('+254700000000', hashed_pin, 'ACC1001', 10000.0, 'Demo User'))
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Helper functions
def get_user_balance(phone_number):
    conn = sqlite3.connect('ussd_database.db')
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE phone_number = ?", (phone_number,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0.0

def get_user_account(phone_number):
    conn = sqlite3.connect('ussd_database.db')
    c = conn.cursor()
    c.execute("SELECT account_number FROM users WHERE phone_number = ?", (phone_number,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def verify_pin(phone_number, pin_input):
    conn = sqlite3.connect('ussd_database.db')
    c = conn.cursor()
    hashed_input = hashlib.sha256(pin_input.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE phone_number = ? AND pin = ?", (phone_number, hashed_input))
    result = c.fetchone()
    conn.close()
    return result is not None

def record_transaction(phone_number, transaction_type, amount, recipient=None):
    conn = sqlite3.connect('ussd_database.db')
    c = conn.cursor()
    c.execute("INSERT INTO transactions (phone_number, transaction_type, amount, recipient) VALUES (?, ?, ?, ?)", 
             (phone_number, transaction_type, amount, recipient))
    conn.commit()
    conn.close()

def get_transaction_history(phone_number, limit=5):
    conn = sqlite3.connect('ussd_database.db')
    c = conn.cursor()
    c.execute("""
        SELECT transaction_type, amount, recipient, timestamp 
        FROM transactions 
        WHERE phone_number = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (phone_number, limit))
    transactions = c.fetchall()
    conn.close()
    return transactions

def transfer_funds(sender, recipient, amount):
    # Simple implementation - in production would include more validation
    conn = sqlite3.connect('ussd_database.db')
    c = conn.cursor()
    
    # Check if recipient exists
    c.execute("SELECT * FROM users WHERE phone_number = ?", (recipient,))
    if not c.fetchone():
        conn.close()
        return False, "Recipient not found"
    
    # Check if sender has enough funds
    c.execute("SELECT balance FROM users WHERE phone_number = ?", (sender,))
    balance = c.fetchone()[0]
    if balance < amount:
        conn.close()
        return False, "Insufficient funds"
    
    # Update balances
    c.execute("UPDATE users SET balance = balance - ? WHERE phone_number = ?", (amount, sender))
    c.execute("UPDATE users SET balance = balance + ? WHERE phone_number = ?", (amount, recipient))
    
    # Record transactions
    record_transaction(sender, "TRANSFER_OUT", amount, recipient)
    record_transaction(recipient, "TRANSFER_IN", amount, sender)
    
    conn.commit()
    conn.close()
    return True, "Transfer successful"

def generate_otp():
    # Generate a simple 6-digit OTP
    return ''.join(random.choices(string.digits, k=6))

@app.route('/ussd', methods=['POST', 'GET'])
def ussd_callback():
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", "default")
    
    # Store session information
    if 'sessions' not in app.config:
        app.config['sessions'] = {}
    
    # Initialize session if new
    if session_id not in app.config['sessions']:
        app.config['sessions'][session_id] = {
            'authenticated': False,
            'pin_attempts': 0,
            'otp': None
        }
    
    # Shortcuts for session data
    session_data = app.config['sessions'][session_id]
    
    # Main menu navigation logic
    if text == '':
        response = "CON Welcome to Mobile Banking\n"
        response += "1. My Account\n"
        response += "2. Money Transfer\n"
        response += "3. Transaction History\n"
        response += "4. Loan Services\n"
        response += "5. Settings"
    
    # Account Information menu
    elif text.startswith('1'):
        # Check authentication for sensitive information
        if not session_data['authenticated'] and not text.startswith('1*0'):
            if text == '1':
                response = "CON Please enter your PIN to access account information"
                return response
            elif len(text.split('*')) == 2:  # PIN entry
                pin_input = text.split('*')[1]
                if verify_pin(phone_number, pin_input):
                    session_data['authenticated'] = True
                    response = "CON Account Information\n"
                    response += "1. Account Number\n"
                    response += "2. Account Balance\n"
                    response += "3. Account Details\n"
                    response += "0. Back to Main Menu"
                else:
                    session_data['pin_attempts'] += 1
                    if session_data['pin_attempts'] >= 3:
                        response = "END Too many incorrect PIN attempts. Please try again later."
                    else:
                        response = f"CON Incorrect PIN. Try again ({3 - session_data['pin_attempts']} attempts left)"
                return response
        
        # User is authenticated, show account submenu or details
        parts = text.split('*')
        if len(parts) == 2 and parts[1] == '1':  # Account Number
            account_number = get_user_account(phone_number)
            response = f"END Your account number is {account_number}"
        elif len(parts) == 2 and parts[1] == '2':  # Account Balance
            balance = get_user_balance(phone_number)
            response = f"END Your balance is KES {balance:,.2f}"
        elif len(parts) == 2 and parts[1] == '3':  # Account Details
            conn = sqlite3.connect('ussd_database.db')
            c = conn.cursor()
            c.execute("SELECT name, account_number, balance FROM users WHERE phone_number = ?", (phone_number,))
            user = c.fetchone()
            conn.close()
            
            if user:
                response = f"END Account Details\n"
                response += f"Name: {user[0]}\n"
                response += f"Account: {user[1]}\n"
                response += f"Balance: KES {user[2]:,.2f}\n"
                response += f"Phone: {phone_number}"
            else:
                response = "END User information not found"
        elif len(parts) == 2 and parts[1] == '0':  # Back to main menu
            response = "CON Welcome to Mobile Banking\n"
            response += "1. My Account\n"
            response += "2. Money Transfer\n"
            response += "3. Transaction History\n"
            response += "4. Loan Services\n"
            response += "5. Settings"
        else:
            response = "CON Account Information\n"
            response += "1. Account Number\n"
            response += "2. Account Balance\n"
            response += "3. Account Details\n"
            response += "0. Back to Main Menu"
    
    # Money Transfer menu
    elif text.startswith('2'):
        if not session_data['authenticated']:
            if text == '2':
                response = "CON Enter your PIN to make a transfer"
                return response
            elif len(text.split('*')) == 2:  # PIN entry
                pin_input = text.split('*')[1]
                if verify_pin(phone_number, pin_input):
                    session_data['authenticated'] = True
                    response = "CON Enter recipient's phone number"
                else:
                    session_data['pin_attempts'] += 1
                    if session_data['pin_attempts'] >= 3:
                        response = "END Too many incorrect PIN attempts. Please try again later."
                    else:
                        response = f"CON Incorrect PIN. Try again ({3 - session_data['pin_attempts']} attempts left)"
                return response
        
        # User is authenticated, proceed with transfer
        parts = text.split('*')
        if len(parts) == 3:  # Recipient entered
            recipient = parts[2]
            response = f"CON Enter amount to send to {recipient}"
        elif len(parts) == 4:  # Amount entered
            recipient = parts[2]
            try:
                amount = float(parts[3])
                # Generate OTP for confirmation
                otp = generate_otp()
                session_data['otp'] = otp
                session_data['transfer'] = {
                    'recipient': recipient,
                    'amount': amount
                }
                response = f"CON You're about to send KES {amount:,.2f} to {recipient}\n"
                response += f"Enter OTP: {otp} to confirm"
            except ValueError:
                response = "END Please enter a valid amount"
        elif len(parts) == 5:  # OTP confirmation
            if session_data.get('otp') and parts[4] == session_data['otp']:
                # Process transfer
                recipient = session_data['transfer']['recipient']
                amount = session_data['transfer']['amount']
                success, message = transfer_funds(phone_number, recipient, amount)
                if success:
                    response = f"END {message}. KES {amount:,.2f} sent to {recipient}"
                else:
                    response = f"END Transfer failed: {message}"
            else:
                response = "END Invalid OTP. Transfer cancelled."
    
    # Transaction History
    elif text.startswith('3'):
        if not session_data['authenticated']:
            if text == '3':
                response = "CON Enter your PIN to view transactions"
                return response
            elif len(text.split('*')) == 2:  # PIN entry
                pin_input = text.split('*')[1]
                if verify_pin(phone_number, pin_input):
                    session_data['authenticated'] = True
                    transactions = get_transaction_history(phone_number)
                    if transactions:
                        response = "END Recent Transactions:\n"
                        for i, (t_type, amount, recipient, timestamp) in enumerate(transactions, 1):
                            date = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                            response += f"{i}. {t_type}: KES {amount:,.2f}"
                            if recipient:
                                response += f" - {recipient}"
                            response += f" ({date})\n"
                    else:
                        response = "END No recent transactions found"
                else:
                    session_data['pin_attempts'] += 1
                    if session_data['pin_attempts'] >= 3:
                        response = "END Too many incorrect PIN attempts. Please try again later."
                    else:
                        response = f"CON Incorrect PIN. Try again ({3 - session_data['pin_attempts']} attempts left)"
                return response
    
    # Loan Services
    elif text.startswith('4'):
        if text == '4':
            response = "CON Loan Services\n"
            response += "1. Check Loan Eligibility\n"
            response += "2. Loan Application\n"
            response += "3. Check Loan Status\n"
            response += "0. Back to Main Menu"
        elif text == '4*1':
            # Simple eligibility check based on account balance
            balance = get_user_balance(phone_number)
            if balance >= 1000:
                loan_limit = balance * 0.5
                response = f"END You are eligible for a loan up to KES {loan_limit:,.2f}"
            else:
                response = "END You are not currently eligible for a loan. Maintain a minimum balance of KES 1,000 to qualify."
        elif text == '4*2':
            response = "END Loan application service coming soon!"
        elif text == '4*3':
            response = "END You have no active loans at this time."
        elif text == '4*0':
            response = "CON Welcome to Mobile Banking\n"
            response += "1. My Account\n"
            response += "2. Money Transfer\n"
            response += "3. Transaction History\n"
            response += "4. Loan Services\n"
            response += "5. Settings"
    
    # Settings menu
    elif text.startswith('5'):
        if text == '5':
            response = "CON Settings\n"
            response += "1. Change PIN\n"
            response += "2. Language Settings\n" 
            response += "3. Register\n"
            response += "0. Back to Main Menu"
        elif text == '5*1':
            response = "END PIN change service coming soon!"
        elif text == '5*2':
            response = "CON Select Language\n"
            response += "1. English\n"
            response += "2. Swahili\n"
            response += "3. French"
        elif text.startswith('5*2*'):
            language_choice = text.split('*')[2]
            languages = {
                '1': 'English',
                '2': 'Swahili',
                '3': 'French'
            }
            if language_choice in languages:
                # In a real application, would update the user's language preference in DB
                response = f"END Language set to {languages[language_choice]}"
            else:
                response = "END Invalid language selection"
        elif text == '5*3':
            response = "END Registration service coming soon!"
        elif text == '5*0':
            response = "CON Welcome to Mobile Banking\n"
            response += "1. My Account\n"
            response += "2. Money Transfer\n"
            response += "3. Transaction History\n"
            response += "4. Loan Services\n"
            response += "5. Settings"
    
    else:
        response = "END Invalid selection. Please try again."
    
    return response

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
