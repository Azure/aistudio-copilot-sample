import {ChatProtocolClient} from "@azure/ai-chat-protocol";
import { AzureKeyCredential } from '@azure/core-auth';

const apiKey = process.env.CHAT_API_KEY;
const endpoint = process.env.CHAT_ENDPOINT;

const credential = new AzureKeyCredential(`Bearer ${apiKey}`);
const options = {
    chatRoute: "/score",
    apiKeyHeader: "Authorization",
};

const client = new ChatProtocolClient(endpoint, credential, options);
console.log("Non-streaming response:");
const response = await client.create([{
    role: "user",
    content: "Hello there!",
}]);
console.log(response.choices[0]?.message?.content);

console.log("Streaming response:");
const stream = await client.createStreaming([{
    role: "user",
    content: "Hello there!",
}]);
for await (const response of stream) {
    console.log(response.choices[0]?.delta?.content);
}
