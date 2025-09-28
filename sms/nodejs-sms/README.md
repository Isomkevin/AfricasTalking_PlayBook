# Node.js SMS Integration with Africa's Talking

This guide details how to build an SMS app using Node.js and Africa's Talking API.

## Prerequisites
- Node.js 18+
- Africa's Talking account and API key

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Isomkevin/AfricasTalking_PlayBook.git
cd AfricasTalking_PlayBook/sms/nodejs-sms
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Project Structure
```
nodejs-sms/
├── index.js
├── package.json
```

### 4. Africa's Talking API Setup
- Register at [Africa's Talking](https://africastalking.com/)
- Get your API key and username
- Add them to your code or use environment variables.

### 5. Sending SMS
- Use the Africa's Talking Node.js SDK in `index.js`:
  ```js
  const AfricasTalking = require('africastalking');

  const africastalking = AfricasTalking({
    apiKey: 'YOUR_API_KEY',
    username: 'YOUR_USERNAME',
  });

  const sms = africastalking.SMS;
  sms.send({
    to: ['+2547xxxxxxx'],
    message: 'Hello from Node.js!',
  }).then(console.log).catch(console.error);
  ```

### 6. Running the App
```bash
node index.js
```

### 7. Testing SMS
- Run the script and check Africa's Talking dashboard for delivery status.

## Troubleshooting
- Ensure API credentials are correct.
- Check Node.js logs for errors.

## Useful Links
- [Africa's Talking Node.js SDK](https://github.com/AfricasTalkingLtd/africastalking-node.js)
- [Node.js Documentation](https://nodejs.org/)

## License
MIT
