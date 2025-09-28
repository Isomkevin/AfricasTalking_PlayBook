# Django USSD Integration with Africa's Talking

This guide provides a detailed walkthrough for building a USSD application using Django and Africa's Talking API.

## Prerequisites
- Python 3.10+
- Django 4.x
- Africa's Talking account and API key

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Isomkevin/AfricasTalking_PlayBook.git
cd AfricasTalking_PlayBook/ussd/django-ussd
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
django_ussd/
├── manage.py
├── ussd/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── ...
├── django_ussd/
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
  # django_ussd/settings.py
  AFRICASTALKING_API_KEY = 'your_api_key'
  AFRICASTALKING_USERNAME = 'your_username'
  ```

### 7. Building a USSD Menu
- Define USSD logic in `views.py`:
  ```python
  def ussd_callback(request):
      session_id = request.GET.get('sessionId')
      service_code = request.GET.get('serviceCode')
      phone_number = request.GET.get('phoneNumber')
      text = request.GET.get('text')
      # USSD menu logic here
      response = "CON Welcome to Django USSD!"
      return HttpResponse(response)
  ```
- Map the view in `urls.py`.

### 8. Expose Endpoint
- Africa's Talking will POST to your endpoint. Use a public URL (e.g., via Ngrok for local dev):
  ```bash
  ngrok http 8000
  ```
- Update Africa's Talking dashboard with your endpoint URL.

### 9. Running the Server
```bash
python manage.py runserver
```

### 10. Testing USSD
- Dial your USSD code and interact with the menu.
- Check Africa's Talking dashboard for session logs.

## Troubleshooting
- Ensure endpoint is publicly accessible.
- Check API credentials and logs.

## Useful Links
- [Africa's Talking USSD Docs](https://africastalking.com/docs/ussd)
- [Django Documentation](https://docs.djangoproject.com/)

## License
MIT
