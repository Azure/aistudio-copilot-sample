## Requirements

Download the chat protocol package.

```powershell
Start-BitsTransfer -Source https://csspeechstorage.blob.core.windows.net/drop/private/ai/azure-ai-chat-protocol-1.0.0-beta.1.tgz
```

```bash
wget https://csspeechstorage.blob.core.windows.net/drop/private/ai/azure-ai-chat-protocol-1.0.0-beta.1.tgz
```

Then install it in your project

```bash
npm install <path-to-your-file>/azure-ai-chat-protocol-1.0.0-beta.1.tgz
```

To run this script, you need to set a couple of environment variables:

```powershell
$env:CHAT_ENDPONT="<your-endpoint>"
$env:CHAT_API_KEY="<your-api-key>"
```
