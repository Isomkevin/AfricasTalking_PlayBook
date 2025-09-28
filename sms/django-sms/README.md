# Django SMS Integration with Africa's Talking

This guide provides a step-by-step walkthrough for building an SMS application using Django and Africa's Talking API.

## Prerequisites
- Python 3.10+
- Django 4.x
- Africa's Talking account and API key

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Isomkevin/AfricasTalking_PlayBook.git
cd AfricasTalking_PlayBook/sms/django-sms
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

### 4. Django Project Structure
```
sms_django/
├── manage.py
├── sms_app/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── ...
├── sms_django/
│   ├── settings.py
│   ├── urls.py
│   └── ...
```

### 5. Database Migration
```bash
python manage.py migrate
```

### 6. Africa's Talking API Setup
- Register at [Africa's Talking](https://africastalking.com/)
- Get your API key and username
- Add them to your Django settings or use environment variables:
  ```python
  # sms_django/settings.py
  AFRICASTALKING_API_KEY = 'your_api_key'
  AFRICASTALKING_USERNAME = 'your_username'
  ```

### 7. Sending SMS
- Use the Africa's Talking Python SDK:
  ```python
  import africastalking

  africastalking.initialize(username, api_key)
  sms = africastalking.SMS
  response = sms.send('Hello from Django!', ['+2547xxxxxxx'])
  print(response)
  ```
- Integrate this logic in your Django view (`views.py`).

### 8. Running the Server
```bash
python manage.py runserver
```

### 9. Testing SMS
- Access the endpoint defined in `urls.py` to trigger SMS sending.
- Check Africa's Talking dashboard for delivery status.

## Troubleshooting
- Ensure your API key and username are correct.
- Check Africa's Talking sandbox vs. production settings.
- Review Django logs for errors.

## Useful Links
- [Africa's Talking Python SDK](https://github.com/AfricasTalkingLtd/africastalking-python)
- [Django Documentation](https://docs.djangoproject.com/)

## License
MIT
