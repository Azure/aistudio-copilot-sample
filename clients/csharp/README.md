## Requirements

Download the chat protocol package.

```powershell
Start-BitsTransfer -Source https://csspeechstorage.blob.core.windows.net/drop/private/ai/Azure.AI.ChatProtocol.1.0.0-alpha.20231105.1.nupkg
```

```bash
wget https://csspeechstorage.blob.core.windows.net/drop/private/ai/Azure.AI.ChatProtocol.1.0.0-alpha.20231105.1.nupkg
```

Then install it in your project

```bash
dotnet add package Azure.AI.ChatProtocol -s <path-to-the-package> --prerelease
```

To run this script, you need to set a couple of environment variables:

```powershell
$env:CHAT_ENDPONT="<your-endpoint>"
$env:CHAT_API_KEY="<your-api-key>"
```
