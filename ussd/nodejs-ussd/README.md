# Node.js USSD Integration with Africa's Talking

This guide details how to build a USSD app using Node.js and Africa's Talking API.

## Prerequisites
- Node.js 18+
- Africa's Talking account and API key

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Isomkevin/AfricasTalking_PlayBook.git
cd AfricasTalking_PlayBook/ussd/nodejs-ussd
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Project Structure
```
nodejs-ussd/
├── index.js
├── package.json
```

### 4. Africa's Talking API Setup
- Register at [Africa's Talking](https://africastalking.com/)
- Get your API key and username
- Add them to your code or use environment variables.

### 5. Building a USSD Menu
- Define USSD logic in `index.js`:
  ```js
  const express = require('express');
  const app = express();
  app.use(express.urlencoded({ extended: true }));

  app.post('/ussd', (req, res) => {
    const { sessionId, serviceCode, phoneNumber, text } = req.body;
    // USSD menu logic here
    res.send('CON Welcome to Node.js USSD!');
  });

  app.listen(3000, () => console.log('USSD server running'));
  ```

### 6. Expose Endpoint
- Africa's Talking will POST to your endpoint. Use a public URL (e.g., via Ngrok for local dev):
  ```bash
  ngrok http 3000
  ```
- Update Africa's Talking dashboard with your endpoint URL.

### 7. Running the App
```bash
node index.js
```

### 8. Testing USSD
- Dial your USSD code and interact with the menu.
- Check Africa's Talking dashboard for session logs.

## Troubleshooting
- Ensure endpoint is publicly accessible.
- Check API credentials and logs.

## Useful Links
- [Africa's Talking USSD Docs](https://africastalking.com/docs/ussd)
- [Node.js Documentation](https://nodejs.org/)

## License
MIT
