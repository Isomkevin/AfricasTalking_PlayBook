# Flask USSD Integration with Africa's Talking

This guide walks you through building a USSD app using Flask and Africa's Talking API.

## Prerequisites
- Python 3.10+
- Flask 2.x
- Africa's Talking account and API key

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Isomkevin/AfricasTalking_PlayBook.git
cd AfricasTalking_PlayBook/ussd/flask-ussd
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
flask-ussd/
├── app.py
├── requirements.txt
```

### 5. Africa's Talking API Setup
- Register at [Africa's Talking](https://africastalking.com/)
- Get your API key and username
- Add them to your Flask config or use environment variables.

### 6. Building a USSD Menu
- Define USSD logic in `app.py`:
  ```python
  @app.route('/ussd', methods=['POST'])
  def ussd():
      session_id = request.values.get('sessionId')
      service_code = request.values.get('serviceCode')
      phone_number = request.values.get('phoneNumber')
      text = request.values.get('text')
      # USSD menu logic here
      response = "CON Welcome to Flask USSD!"
      return response
  ```

### 7. Expose Endpoint
- Africa's Talking will POST to your endpoint. Use a public URL (e.g., via Ngrok for local dev):
  ```bash
  ngrok http 5000
  ```
- Update Africa's Talking dashboard with your endpoint URL.

### 8. Running the Server
```bash
python app.py
```

### 9. Testing USSD
- Dial your USSD code and interact with the menu.
- Check Africa's Talking dashboard for session logs.

## Troubleshooting
- Ensure endpoint is publicly accessible.
- Check API credentials and logs.

## Useful Links
- [Africa's Talking USSD Docs](https://africastalking.com/docs/ussd)
- [Flask Documentation](https://flask.palletsprojects.com/)

## License
MIT
