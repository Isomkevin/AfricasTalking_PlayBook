# Node.js Voice Integration with Africa's Talking

This guide details how to build a voice call app using Node.js and Africa's Talking API.

## Prerequisites
- Node.js 18+
- Africa's Talking account and API key

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Isomkevin/AfricasTalking_PlayBook.git
cd AfricasTalking_PlayBook/voice/nodejs-voice
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Project Structure
```
nodejs-voice/
├── src/
│   └── server.js
├── package.json
```

### 4. Africa's Talking API Setup
- Register at [Africa's Talking](https://africastalking.com/)
- Get your API key and username
- Add them to your code or use environment variables.

### 5. Making Voice Calls
- Use the Africa's Talking Node.js SDK in `src/server.js`:
  ```js
  const AfricasTalking = require('africastalking');

  const africastalking = AfricasTalking({
    apiKey: 'YOUR_API_KEY',
    username: 'YOUR_USERNAME',
  });

  const voice = africastalking.Voice;
  voice.call({
    callFrom: '+2547xxxxxxx',
    callTo: ['+2547yyyyyyy'],
  }).then(console.log).catch(console.error);
  ```

### 6. Running the App
```bash
node src/server.js
```

### 7. Testing Voice Calls
- Run the script and check Africa's Talking dashboard for call status.

## Troubleshooting
- Ensure API credentials are correct.
- Check Node.js logs for errors.

## Useful Links
- [Africa's Talking Node.js SDK](https://github.com/AfricasTalkingLtd/africastalking-node.js)
- [Node.js Documentation](https://nodejs.org/)

## License
MIT
