# AfricasTalking PlayBook

This repository provides a comprehensive set of code samples and starter projects for integrating with Africa's Talking APIs across multiple channels and frameworks. It is organized by communication channel (SMS, USSD, Voice) and by backend technology (Django, Flask, Node.js, TypeScript).

## Table of Contents
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Channel & Framework Guides](#channel--framework-guides)
  - [SMS](#sms)
  - [USSD](#ussd)
  - [Voice](#voice)
- [Contributing](#contributing)
- [License](#license)

---

## Project Structure

```
AfricasTalking_PlayBook/
├── sms/
│   ├── django-sms/
│   ├── flask-sms/
│   ├── nodejs-sms/
│   └── typescript-sms/
├── ussd/
│   ├── django-ussd/
│   ├── flask-ussd/
│   └── nodejs-ussd/
├── voice/
│   ├── django-voice/
│   ├── flask-voice/
│   ├── nodejs-voice/
│   ├── nodejs-voice2/
│   └── typescript-voice/
└── Readme.md
```

Each channel (SMS, USSD, Voice) contains subfolders for different backend frameworks. Each subproject is self-contained with its own dependencies and instructions.

---

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Isomkevin/AfricasTalking_PlayBook.git
   cd AfricasTalking_PlayBook
   ```
2. **Navigate to the desired channel and framework:**
   ```bash
   cd sms/django-sms
   # or
   cd ussd/nodejs-ussd
   ```
3. **Follow the README or instructions in each subproject for setup and running.**

---

## Channel & Framework Guides

### SMS
- **Django:** `sms/django-sms/`
  - Python/Django project for sending and receiving SMS using Africa's Talking.
  - Setup: See `requirements.txt` and `sms_django/README.md` (if available).
- **Flask:** `sms/flask-sms/`
  - Lightweight Flask app for SMS integration.
  - Setup: See `requirements.txt` and `ReadMe.md`.
- **Node.js:** `sms/nodejs-sms/`
  - Node.js example for SMS APIs.
  - Setup: See `package.json`.
- **TypeScript:** `sms/typescript-sms/`
  - TypeScript starter for SMS.
  - Setup: See `package.json` and `tsconfig.json`.

### USSD
- **Django:** `ussd/django-ussd/`
  - Django project for USSD menu integration.
  - Setup: See `requirements.txt`.
- **Flask:** `ussd/flask-ussd/`
  - Flask app for USSD.
  - Setup: See `requirements.txt` and `Readme.md`.
- **Node.js:** `ussd/nodejs-ussd/`
  - Node.js USSD integration.
  - Setup: See `package.json`.

### Voice
- **Django:** `voice/django-voice/`
  - Django project for voice call integration.
  - Setup: See `requirements.txt`.
- **Flask:** `voice/flask-voice/`
  - Flask app for voice APIs.
  - Setup: See `requirements.txt` and `Readme.md`.
- **Node.js:** `voice/nodejs-voice/` and `voice/nodejs-voice2/`
  - Node.js voice call examples.
  - Setup: See `package.json`.
- **TypeScript:** `voice/typescript-voice/`
  - TypeScript voice integration.
  - Setup: See `package.json` and `tsconfig.json`.

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request. For major changes, open an issue first to discuss what you would like to change.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## About Africa's Talking

[Africa's Talking](https://africastalking.com/) provides APIs for SMS, USSD, Voice, Airtime, Payments, and more, enabling developers to build scalable communication solutions across Africa.

---

## Contact

For questions or support, please open an issue or contact the repository owner.
