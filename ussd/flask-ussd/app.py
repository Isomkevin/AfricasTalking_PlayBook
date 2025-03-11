from flask import Flask, request
import os
import sqlite3
import datetime
import hashlib
import random
import string
import functools
from contextlib import contextmanager
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'ussd_secret_key'  # For session management
CORS(app)

# Database setup and context manager
@contextmanager
def get_db_connection():
    conn = sqlite3.connect('ussd_database.db')
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
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
        c.execute("SELECT * FROM users WHERE phone_number = '+254758750620'")
        if not c.fetchone():
            # Store PIN as hashed value (using simple hash for demo)
            hashed_pin = hashlib.sha256('1234'.encode()).hexdigest()
            c.execute("INSERT INTO users (phone_number, pin, account_number, balance, name) VALUES (?, ?, ?, ?, ?)", 
                     ('+254758750620', hashed_pin, 'ACC1001', 10000.0, 'Demo User'))

# Initialize database
init_db()

# Helper functions
def get_user_balance(phone_number):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE phone_number = ?", (phone_number,))
        result = c.fetchone()
    return result[0] if result else 0.0

def get_user_account(phone_number):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT account_number FROM users WHERE phone_number = ?", (phone_number,))
        result = c.fetchone()
    return result[0] if result else None

def get_user_details(phone_number):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT name, account_number, balance FROM users WHERE phone_number = ?", (phone_number,))
        return c.fetchone()

def verify_pin(phone_number, pin_input):
    with get_db_connection() as conn:
        c = conn.cursor()
        hashed_input = hashlib.sha256(pin_input.encode()).hexdigest()
        c.execute("SELECT * FROM users WHERE phone_number = ? AND pin = ?", (phone_number, hashed_input))
        result = c.fetchone()
    return result is not None

def record_transaction(phone_number, transaction_type, amount, recipient=None):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO transactions (phone_number, transaction_type, amount, recipient) VALUES (?, ?, ?, ?)", 
                 (phone_number, transaction_type, amount, recipient))

def get_transaction_history(phone_number, limit=5):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT transaction_type, amount, recipient, timestamp 
            FROM transactions 
            WHERE phone_number = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (phone_number, limit))
        return c.fetchall()

def check_recipient_exists(recipient):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE phone_number = ?", (recipient,))
        return c.fetchone() is not None

def transfer_funds(sender, recipient, amount):
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # Check if recipient exists
        if not check_recipient_exists(recipient):
            return False, "Recipient not found"
        
        # Check if sender has enough funds
        c.execute("SELECT balance FROM users WHERE phone_number = ?", (sender,))
        balance = c.fetchone()[0]
        if balance < amount:
            return False, "Insufficient funds"
        
        # Update balances
        c.execute("UPDATE users SET balance = balance - ? WHERE phone_number = ?", (amount, sender))
        c.execute("UPDATE users SET balance = balance + ? WHERE phone_number = ?", (amount, recipient))
    
    # Record transactions
    record_transaction(sender, "TRANSFER_OUT", amount, recipient)
    record_transaction(recipient, "TRANSFER_IN", amount, sender)
    
    return True, "Transfer successful"

def generate_otp():
    # Generate a simple 6-digit OTP
    return ''.join(random.choices(string.digits, k=6))

def get_ussd_params(request):
    return {
        "session_id": request.values.get("sessionId", None),
        "service_code": request.values.get("serviceCode", None),
        "phone_number": request.values.get("phoneNumber", None),
        "text": request.values.get("text", "default")
    }

def get_session_data(session_id):
    if 'sessions' not in app.config:
        app.config['sessions'] = {}
    
    if session_id not in app.config['sessions']:
        app.config['sessions'][session_id] = {
            'authenticated': False,
            'pin_attempts': 0,
            'otp': None
        }
    
    return app.config['sessions'][session_id]

def authenticate_user(session_data, phone_number, pin_input=None):
    if session_data.get('authenticated', False):
        return True, None
    
    if pin_input is None:
        return False, "CON Please enter your PIN to continue"
    
    if verify_pin(phone_number, pin_input):
        session_data['authenticated'] = True
        return True, None
    else:
        session_data['pin_attempts'] = session_data.get('pin_attempts', 0) + 1
        if session_data.get('pin_attempts', 0) >= 3:
            return False, "END Too many incorrect PIN attempts. Please try again later."
        else:
            return False, f"CON Incorrect PIN. Try again ({3 - session_data.get('pin_attempts', 0)} attempts left)"

# Menu text generators
def get_main_menu():
    return ("CON Welcome to Mobile Banking\n"
            "1. My Account\n"
            "2. Money Transfer\n"
            "3. Transaction History\n"
            "4. Loan Services\n"
            "5. Settings")

def get_account_menu():
    return ("CON Account Information\n"
            "1. Account Number\n"
            "2. Account Balance\n"
            "3. Account Details\n"
            "0. Back to Main Menu")

def get_loan_menu():
    return ("CON Loan Services\n"
            "1. Check Loan Eligibility\n"
            "2. Loan Application\n"
            "3. Check Loan Status\n"
            "0. Back to Main Menu")

def get_settings_menu():
    return ("CON Settings\n"
            "1. Change PIN\n"
            "2. Language Settings\n" 
            "3. Register\n"
            "0. Back to Main Menu")

def get_language_menu():
    return ("CON Select Language\n"
            "1. English\n"
            "2. Swahili\n"
            "3. French")

# Menu handlers
def handle_account_menu(parts, phone_number, session_data):
    # First check authentication
    if not session_data.get('authenticated', False):
        if len(parts) == 1:  # Just '1'
            return "CON Please enter your PIN to access account information"
        elif len(parts) == 2:  # PIN entry
            auth_success, auth_message = authenticate_user(session_data, phone_number, parts[1])
            if auth_message:
                return auth_message
            return get_account_menu()
    
    # User is authenticated
    if len(parts) == 2:
        if parts[1] == '1':  # Account Number
            account_number = get_user_account(phone_number)
            return f"END Your account number is {account_number}"
        elif parts[1] == '2':  # Account Balance
            balance = get_user_balance(phone_number)
            return f"END Your balance is KES {balance:,.2f}"
        elif parts[1] == '3':  # Account Details
            user = get_user_details(phone_number)
            if user:
                return (f"END Account Details\n"
                        f"Name: {user[0]}\n"
                        f"Account: {user[1]}\n"
                        f"Balance: KES {user[2]:,.2f}\n"
                        f"Phone: {phone_number}")
            else:
                return "END User information not found"
        elif parts[1] == '0':  # Back to main menu
            return get_main_menu()
    
    return get_account_menu()

def handle_transfer_menu(parts, phone_number, session_data):
    # First check authentication
    if not session_data.get('authenticated', False):
        if len(parts) == 1:  # Just '2'
            return "CON Enter your PIN to make a transfer"
        elif len(parts) == 2:  # PIN entry
            auth_success, auth_message = authenticate_user(session_data, phone_number, parts[1])
            if auth_message:
                return auth_message
            return "CON Enter recipient's phone number"
    
    # User is authenticated
    if len(parts) == 3:  # Recipient entered
        recipient = parts[2]
        return f"CON Enter amount to send to {recipient}"
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
            return (f"CON You're about to send KES {amount:,.2f} to {recipient}\n"
                    f"Enter OTP: {otp} to confirm")
        except ValueError:
            return "END Please enter a valid amount"
    elif len(parts) == 5:  # OTP confirmation
        if session_data.get('otp') and parts[4] == session_data.get('otp'):
            # Process transfer
            recipient = session_data.get('transfer', {}).get('recipient')
            amount = session_data.get('transfer', {}).get('amount')
            if recipient and amount:
                success, message = transfer_funds(phone_number, recipient, amount)
                if success:
                    return f"END {message}. KES {amount:,.2f} sent to {recipient}"
                else:
                    return f"END Transfer failed: {message}"
            else:
                return "END Transfer information missing. Please try again."
        else:
            return "END Invalid OTP. Transfer cancelled."
    
    return "CON Money Transfer\nPlease follow the prompts to complete your transfer."

def handle_transaction_history_menu(parts, phone_number, session_data):
    # First check authentication
    if not session_data.get('authenticated', False):
        if len(parts) == 1:  # Just '3'
            return "CON Enter your PIN to view transactions"
        elif len(parts) == 2:  # PIN entry
            auth_success, auth_message = authenticate_user(session_data, phone_number, parts[1])
            if auth_message:
                return auth_message
            # Show transaction history immediately after authentication
            transactions = get_transaction_history(phone_number)
            if transactions:
                response = "END Recent Transactions:\n"
                for i, (t_type, amount, recipient, timestamp) in enumerate(transactions, 1):
                    date = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                    response += f"{i}. {t_type}: KES {amount:,.2f}"
                    if recipient:
                        response += f" - {recipient}"
                    response += f" ({date})\n"
                return response
            else:
                return "END No recent transactions found"
    
    return "CON Transaction History feature is being accessed"

def handle_loan_menu(parts, phone_number, session_data):
    if len(parts) == 1:  # Just '4'
        return get_loan_menu()
    elif len(parts) == 2:
        if parts[1] == '1':  # Check Loan Eligibility
            balance = get_user_balance(phone_number)
            if balance >= 1000:
                loan_limit = balance * 0.5
                return f"END You are eligible for a loan up to KES {loan_limit:,.2f}"
            else:
                return "END You are not currently eligible for a loan. Maintain a minimum balance of KES 1,000 to qualify."
        elif parts[1] == '2':  # Loan Application
            return "END Loan application service coming soon!"
        elif parts[1] == '3':  # Check Loan Status
            return "END You have no active loans at this time."
        elif parts[1] == '0':  # Back to main menu
            return get_main_menu()
    
    return get_loan_menu()

def handle_settings_menu(parts, phone_number, session_data):
    if len(parts) == 1:  # Just '5'
        return get_settings_menu()
    elif len(parts) == 2:
        if parts[1] == '1':  # Change PIN
            return "END PIN change service coming soon!"
        elif parts[1] == '2':  # Language Settings
            return get_language_menu()
        elif parts[1] == '3':  # Register
            return "END Registration service coming soon!"
        elif parts[1] == '0':  # Back to main menu
            return get_main_menu()
    elif len(parts) >= 3 and parts[1] == '2':  # Language selection
        language_choice = parts[2]
        languages = {
            '1': 'English',
            '2': 'Swahili',
            '3': 'French'
        }
        if language_choice in languages:
            # In a real application, would update the user's language preference in DB
            return f"END Language set to {languages[language_choice]}"
        else:
            return "END Invalid language selection"
    
    return get_settings_menu()

# Error handling decorator
def ussd_error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            app.logger.error(f"Error in USSD callback: {str(e)}")
            return "END An error occurred. Please try again later."
    return wrapper

@app.route('/ussd', methods=['POST', 'GET'])
@ussd_error_handler
def ussd_callback():
    # Extract parameters
    params = get_ussd_params(request)
    session_id = params["session_id"]
    phone_number = params["phone_number"]
    text = params["text"]
    
    # Get session data
    session_data = get_session_data(session_id)
    
    # Main menu navigation logic
    if text == '':
        return get_main_menu()
    
    # Split the text into parts
    parts = text.split('*')
    first_part = parts[0] if parts else ''
    
    # Route to appropriate handler based on first digit
    if first_part == '1':
        return handle_account_menu(parts, phone_number, session_data)
    elif first_part == '2':
        return handle_transfer_menu(parts, phone_number, session_data)
    elif first_part == '3':
        return handle_transaction_history_menu(parts, phone_number, session_data)
    elif first_part == '4':
        return handle_loan_menu(parts, phone_number, session_data)
    elif first_part == '5':
        return handle_settings_menu(parts, phone_number, session_data)
    else:
        return "END Invalid selection. Please try again."

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
