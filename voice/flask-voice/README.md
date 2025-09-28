# Flask Voice Integration with Africa's Talking

This guide walks you through building a voice call app using Flask and Africa's Talking API.

## Prerequisites
- Python 3.10+
- Flask 2.x
- Africa's Talking account and API key

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Isomkevin/AfricasTalking_PlayBook.git
cd AfricasTalking_PlayBook/voice/flask-voice
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
flask-voice/
├── app.py
├── main.py
├── requirements.txt
```

### 5. Africa's Talking API Setup
- Register at [Africa's Talking](https://africastalking.com/)
- Get your API key and username
- Add them to your Flask config or use environment variables.

### 6. Making Voice Calls
- Use the Africa's Talking Python SDK in `app.py` or `main.py`:
  ```python
  import africastalking

  africastalking.initialize(username, api_key)
  voice = africastalking.Voice
  response = voice.call({
      'callFrom': '+2547xxxxxxx',
      'callTo': ['+2547yyyyyyy']
  })
  print(response)
  ```
- Create a Flask route to trigger voice calls.

### 7. Running the Server
```bash
python app.py
```

### 8. Testing Voice Calls
- Access the endpoint in your browser or via curl to initiate a call.
- Check Africa's Talking dashboard for call status.

## Troubleshooting
- Verify API credentials.
- Check Flask logs for errors.

## Useful Links
- [Africa's Talking Python SDK](https://github.com/AfricasTalkingLtd/africastalking-python)
- [Flask Documentation](https://flask.palletsprojects.com/)

## License
MIT
