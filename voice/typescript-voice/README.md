# TypeScript Voice Integration with Africa's Talking

This guide explains how to build a voice call app using TypeScript and Africa's Talking API.

## Prerequisites
- Node.js 18+
- TypeScript 5.x
- Africa's Talking account and API key

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Isomkevin/AfricasTalking_PlayBook.git
cd AfricasTalking_PlayBook/voice/typescript-voice
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Project Structure
```
typescript-voice/
├── src/
│   └── server.ts
├── package.json
├── tsconfig.json
```

### 4. Africa's Talking API Setup
- Register at [Africa's Talking](https://africastalking.com/)
- Get your API key and username
- Store them in environment variables or a config file.

### 5. Making Voice Calls
- Use the Africa's Talking Node.js SDK in `src/server.ts`:
  ```ts
  import AfricasTalking from 'africastalking';

  const africastalking = AfricasTalking({
    apiKey: process.env.AT_API_KEY!,
    username: process.env.AT_USERNAME!,
  });

  const voice = africastalking.Voice;
  voice.call({
    callFrom: '+2547xxxxxxx',
    callTo: ['+2547yyyyyyy'],
  }).then(console.log).catch(console.error);
  ```

### 6. Running the App
```bash
npx ts-node src/server.ts
```

### 7. Testing Voice Calls
- Run the script and check Africa's Talking dashboard for call status.

## Troubleshooting
- Ensure API credentials are set in environment variables.
- Check TypeScript logs for errors.

## Useful Links
- [Africa's Talking Node.js SDK](https://github.com/AfricasTalkingLtd/africastalking-node.js)
- [TypeScript Documentation](https://www.typescriptlang.org/)

## License
MIT
