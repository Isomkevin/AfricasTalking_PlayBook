# Flask SMS Integration with Africa's Talking

This guide walks you through building an SMS app using Flask and Africa's Talking API.

## Prerequisites
- Python 3.10+
- Flask 2.x
- Africa's Talking account and API key

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Isomkevin/AfricasTalking_PlayBook.git
cd AfricasTalking_PlayBook/sms/flask-sms
```

### 2. Create and Activate a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Project Structure
```
flask-sms/
├── app.py
├── requirements.txt
```

### 5. Africa's Talking API Setup
- Register at [Africa's Talking](https://africastalking.com/)
- Get your API key and username
- Add them to your Flask config or use environment variables.

### 6. Sending SMS
- Use the Africa's Talking Python SDK in `app.py`:
  ```python
  import africastalking

  africastalking.initialize(username, api_key)
  sms = africastalking.SMS
  response = sms.send('Hello from Flask!', ['+2547xxxxxxx'], sender_id="AFTKNG"  # your Alphanumeric sender ID)
  print(response)
  ```
- Create a Flask route to trigger SMS sending.

### 7. Running the Server
```bash
python app.py
```

### 8. Testing SMS
- Access the endpoint in your browser or via curl to send SMS.
- Check Africa's Talking dashboard for delivery status.

## Troubleshooting
- Verify API credentials.
- Check Flask logs for errors.

## Useful Links
- [Africa's Talking Python SDK](https://github.com/AfricasTalkingLtd/africastalking-python)
- [Flask Documentation](https://flask.palletsprojects.com/)

## License
MIT
