using Azure;
using Azure.AI.ChatProtocol;

public static class Program
{
    private static string apiKey = Environment.GetEnvironmentVariable("CHAT_API_KEY") ?? throw new Exception("CHAT_API_KEY not set");
    private static string endpoint = Environment.GetEnvironmentVariable("CHAT_ENDPOINT") ?? throw new Exception("CHAT_ENDPOINT not set");

    public static void Main(string[] args)
    {
        AzureKeyCredential credential = new($"Bearer {apiKey}");

        ChatProtocolClientOptions options = new()
        {
            ChatRoute = "/score",
            APIKeyHeader = "Authorization"
        };
        ChatProtocolClient client = new(new(endpoint), credential, options);

        Console.WriteLine("Non-streaming response:");
        ChatCompletion completion = client.Create(new ChatCompletionOptions(new List<ChatMessage>
        {
            new TextChatMessage(ChatRole.User, "Hello there!"),
        }));
        if (completion.Choices[0].Message is TextChatMessage textChatMessage)
        {
            Console.WriteLine(textChatMessage.Content);
        }

        Console.WriteLine("Streaming response:");
        var response = client.CreateStreaming(new StreamingChatCompletionOptions(new List<ChatMessage>
        {
            new TextChatMessage(ChatRole.User, "Hello there!"),
        }));
        IEnumerable<ChatCompletionChunk> chunks = response.Value;
        foreach (ChatCompletionChunk chunk in chunks)
        {
            if (chunk.Choices[0].Delta is TextChatMessageDelta textChatMessageDelta)
            {
                Console.WriteLine(textChatMessageDelta.Content);
            }
        }
    }
}

