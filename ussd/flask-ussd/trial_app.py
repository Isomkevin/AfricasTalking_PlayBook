# File structure:
# - app.py (main application file)
# - database.py (database operations)
# - ussd_handler.py (USSD menu logic)
# - utils.py (utility functions)

# ======== app.py ========
from flask import Flask
from flask_cors import CORS
from database import init_db
from ussd_handler import ussd_route

app = Flask(__name__)
app.secret_key = 'ussd_secret_key'  # For session management
CORS(app)

# Initialize database
init_db()

# Register the USSD route
app.register_blueprint(ussd_route)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)

# ======== database.py ========
import sqlite3
import hashlib

def init_db():
    """Initialize the database with necessary tables and demo data."""
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

def get_user_balance(phone_number):
    """Get user's account balance."""
    conn = sqlite3.connect('ussd_database.db')
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE phone_number = ?", (phone_number,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0.0

def get_user_account(phone_number):
    """Get user's account number."""
    conn = sqlite3.connect('ussd_database.db')
    c = conn.cursor()
    c.execute("SELECT account_number FROM users WHERE phone_number = ?", (phone_number,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_user_details(phone_number):
    """Get user's complete details."""
    conn = sqlite3.connect('ussd_database.db')
    c = conn.cursor()
    c.execute("SELECT name, account_number, balance FROM users WHERE phone_number = ?", (phone_number,))
    user = c.fetchone()
    conn.close()
    return user

def verify_pin(phone_number, pin_input):
    """Verify if the PIN matches for the given phone number."""
    conn = sqlite3.connect('ussd_database.db')
    c = conn.cursor()
    hashed_input = hashlib.sha256(pin_input.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE phone_number = ? AND pin = ?", (phone_number, hashed_input))
    result = c.fetchone()
    conn.close()
    return result is not None

def record_transaction(phone_number, transaction_type, amount, recipient=None):
    """Record a transaction in the database."""
    conn = sqlite3.connect('ussd_database.db')
    c = conn.cursor()
    c.execute("INSERT INTO transactions (phone_number, transaction_type, amount, recipient) VALUES (?, ?, ?, ?)", 
             (phone_number, transaction_type, amount, recipient))
    conn.commit()
    conn.close()

def get_transaction_history(phone_number, limit=5):
    """Get recent transaction history for a user."""
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
    """Transfer funds between accounts."""
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

# ======== utils.py ========
import random
import string
import datetime

def generate_otp():
    """Generate a 6-digit OTP."""
    return ''.join(random.choices(string.digits, k=6))

def format_date(date_str):
    """Format date string for display."""
    return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")

def format_currency(amount):
    """Format amount as currency."""
    return f"KES {amount:,.2f}"

# ======== ussd_handler.py ========
from flask import Blueprint, request, current_app
import datetime
from database import (
    get_user_balance, get_user_account, get_user_details,
    verify_pin, get_transaction_history, transfer_funds
)
from utils import generate_otp, format_date

# Create a blueprint for USSD routes
ussd_route = Blueprint('ussd', __name__)

# Menu handlers
def handle_main_menu():
    """Generate main menu response."""
    response = "CON Welcome to Mobile Banking\n"
    response += "1. My Account\n"
    response += "2. Money Transfer\n"
    response += "3. Transaction History\n"
    response += "4. Loan Services\n"
    response += "5. Settings"
    return response

def handle_account_menu(text, phone_number, session_data):
    """Handle account menu options."""
    # Check authentication for sensitive information
    if not session_data.get('authenticated', False) and not text.startswith('1*0'):
        if text == '1':
            return "CON Please enter your PIN to access account information"
        elif len(text.split('*')) == 2:  # PIN entry
            pin_input = text.split('*')[1]
            if verify_pin(phone_number, pin_input):
                session_data['authenticated'] = True
                return account_submenu()
            else:
                session_data['pin_attempts'] = session_data.get('pin_attempts', 0) + 1
                if session_data.get('pin_attempts', 0) >= 3:
                    return "END Too many incorrect PIN attempts. Please try again later."
                else:
                    return f"CON Incorrect PIN. Try again ({3 - session_data.get('pin_attempts', 0)} attempts left)"
    
    # User is authenticated, show account submenu or details
    parts = text.split('*')
    if len(parts) == 2 and parts[1] == '1':  # Account Number
        account_number = get_user_account(phone_number)
        return f"END Your account number is {account_number}"
    elif len(parts) == 2 and parts[1] == '2':  # Account Balance
        balance = get_user_balance(phone_number)
        return f"END Your balance is KES {balance:,.2f}"
    elif len(parts) == 2 and parts[1] == '3':  # Account Details
        user = get_user_details(phone_number)
        if user:
            response = f"END Account Details\n"
            response += f"Name: {user[0]}\n"
            response += f"Account: {user[1]}\n"
            response += f"Balance: KES {user[2]:,.2f}\n"
            response += f"Phone: {phone_number}"
            return response
        else:
            return "END User information not found"
    elif len(parts) == 2 and parts[1] == '0':  # Back to main menu
        return handle_main_menu()
    else:
        return account_submenu()

def account_submenu():
    """Generate account submenu response."""
    response = "CON Account Information\n"
    response += "1. Account Number\n"
    response += "2. Account Balance\n"
    response += "3. Account Details\n"
    response += "0. Back to Main Menu"
    return response

def handle_transfer_menu(text, phone_number, session_data):
    """Handle money transfer menu options."""
    if not session_data.get('authenticated', False):
        if text == '2':
            return "CON Enter your PIN to make a transfer"
        elif len(text.split('*')) == 2:  # PIN entry
            pin_input = text.split('*')[1]
            if verify_pin(phone_number, pin_input):
                session_data['authenticated'] = True
                return "CON Enter recipient's phone number"
            else:
                session_data['pin_attempts'] = session_data.get('pin_attempts', 0) + 1
                if session_data.get('pin_attempts', 0) >= 3:
                    return "END Too many incorrect PIN attempts. Please try again later."
                else:
                    return f"CON Incorrect PIN. Try again ({3 - session_data.get('pin_attempts', 0)} attempts left)"
    
    # User is authenticated, proceed with transfer
    parts = text.split('*')
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
            response = f"CON You're about to send KES {amount:,.2f} to {recipient}\n"
            response += f"Enter OTP: {otp} to confirm"
            return response
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
    else:
        return "CON Money Transfer\nPlease follow the prompts to complete your transfer."

def handle_transaction_history(text, phone_number, session_data):
    """Handle transaction history menu options."""
    if not session_data.get('authenticated', False):
        if text == '3':
            return "CON Enter your PIN to view transactions"
        elif len(text.split('*')) == 2:  # PIN entry
            pin_input = text.split('*')[1]
            if verify_pin(phone_number, pin_input):
                session_data['authenticated'] = True
                transactions = get_transaction_history(phone_number)
                if transactions:
                    response = "END Recent Transactions:\n"
                    for i, (t_type, amount, recipient, timestamp) in enumerate(transactions, 1):
                        date = format_date(timestamp)
                        response += f"{i}. {t_type}: KES {amount:,.2f}"
                        if recipient:
                            response += f" - {recipient}"
                        response += f" ({date})\n"
                    return response
                else:
                    return "END No recent transactions found"
            else:
                session_data['pin_attempts'] = session_data.get('pin_attempts', 0) + 1
                if session_data.get('pin_attempts', 0) >= 3:
                    return "END Too many incorrect PIN attempts. Please try again later."
                else:
                    return f"CON Incorrect PIN. Try again ({3 - session_data.get('pin_attempts', 0)} attempts left)"
    return "CON Transaction History feature is being accessed"

def handle_loan_menu(text, phone_number):
    """Handle loan services menu options."""
    if text == '4':
        response = "CON Loan Services\n"
        response += "1. Check Loan Eligibility\n"
        response += "2. Loan Application\n"
        response += "3. Check Loan Status\n"
        response += "0. Back to Main Menu"
        return response
    elif text == '4*1':
        # Simple eligibility check based on account balance
        balance = get_user_balance(phone_number)
        if balance >= 1000:
            loan_limit = balance * 0.5
            return f"END You are eligible for a loan up to KES {loan_limit:,.2f}"
        else:
            return "END You are not currently eligible for a loan. Maintain a minimum balance of KES 1,000 to qualify."
    elif text == '4*2':
        return "END Loan application service coming soon!"
    elif text == '4*3':
        return "END You have no active loans at this time."
    elif text == '4*0':
        return handle_main_menu()
    return "END Invalid loan service selection"

def handle_settings_menu(text):
    """Handle settings menu options."""
    if text == '5':
        response = "CON Settings\n"
        response += "1. Change PIN\n"
        response += "2. Language Settings\n" 
        response += "3. Register\n"
        response += "0. Back to Main Menu"
        return response
    elif text == '5*1':
        return "END PIN change service coming soon!"
    elif text == '5*2':
        response = "CON Select Language\n"
        response += "1. English\n"
        response += "2. Swahili\n"
        response += "3. French"
        return response
    elif text.startswith('5*2*'):
        language_choice = text.split('*')[2]
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
    elif text == '5*3':
        return "END Registration service coming soon!"
    elif text == '5*0':
        return handle_main_menu()
    return "END Invalid settings selection"

@ussd_route.route('/ussd', methods=['POST', 'GET'])
def ussd_callback():
    """USSD callback handler function."""
    # Initialize response to handle all possible code paths
    response = "END An error occurred. Please try again."
    
    try:
        session_id = request.values.get("sessionId", None)
        service_code = request.values.get("serviceCode", None)
        phone_number = request.values.get("phoneNumber", None)
        text = request.values.get("text", "default")
        
        # Store session information
        if 'sessions' not in current_app.config:
            current_app.config['sessions'] = {}
        
        # Initialize session if new
        if session_id not in current_app.config['sessions']:
            current_app.config['sessions'][session_id] = {
                'authenticated': False,
                'pin_attempts': 0,
                'otp': None
            }
        
        # Shortcuts for session data
        session_data = current_app.config['sessions'][session_id]
        
        # Main menu navigation logic
        if text == '':
            response = handle_main_menu()
        
        # Account Information menu
        elif text.startswith('1'):
            response = handle_account_menu(text, phone_number, session_data)
        
        # Money Transfer menu
        elif text.startswith('2'):
            response = handle_transfer_menu(text, phone_number, session_data)
        
        # Transaction History
        elif text.startswith('3'):
            response = handle_transaction_history(text, phone_number, session_data)
        
        # Loan Services
        elif text.startswith('4'):
            response = handle_loan_menu(text, phone_number)
        
        # Settings menu
        elif text.startswith('5'):
            response = handle_settings_menu(text)
        
        else:
            response = "END Invalid selection. Please try again."
            
    except Exception as e:
        # Log the error
        current_app.logger.error(f"Error in USSD callback: {str(e)}")
        response = "END An error occurred. Please try again later."
    
    return response
