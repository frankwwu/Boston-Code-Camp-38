using DotNetEnv;
using System.Reflection;
using System.Text;
using System.Text.Json;

namespace Llama_Together_AI
{
    class Program
    {
        private static string apiKey = string.Empty;
        private static string model = string.Empty;
        private static List<(string Role, string Content)> chatHistory = new List<(string, string)>();

        static async Task Main()
        {
            Env.Load();
            apiKey = Env.GetString("TOGETHER_API_KEY");
            model = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free";

            while (true)
            {
                Console.Write("\nQuestion: ");

                var prompt = Console.ReadLine();
                if (string.IsNullOrWhiteSpace(prompt))
                {
                    break;
                }

                chatHistory.Add(("user", prompt));

                string response = await GetTogetherAIResponse();
                Console.WriteLine(response);

                chatHistory.Add(("assistant", response));
                Console.WriteLine();
            }
        }

        static async Task<string> GetTogetherAIResponse()
        {
            using HttpClient client = new HttpClient();
            client.DefaultRequestHeaders.Add("Authorization", $"Bearer {apiKey}");

            var messages = chatHistory.Select(item => new { role = item.Role, content = item.Content }).ToArray();

            var requestBody = new
            {
                model = model,
                messages = messages,
                max_tokens = 1200,
                temperature = 0.25
            };

            string jsonBody = JsonSerializer.Serialize(requestBody);
            var content = new StringContent(jsonBody, Encoding.UTF8, "application/json");

            HttpResponseMessage response = await client.PostAsync("https://api.together.ai/v1/chat/completions", content);
            if (response.IsSuccessStatusCode)
            {
                string responseString = await response.Content.ReadAsStringAsync();
                using JsonDocument doc = JsonDocument.Parse(responseString);
                JsonElement root = doc.RootElement;

                if (root.TryGetProperty("choices", out JsonElement choices) && choices.GetArrayLength() > 0)
                {
                    return choices[0].GetProperty("message").GetProperty("content").GetString() ?? "No response received.";
                }
            }

            return $"Error: {response.StatusCode} - {response.ReasonPhrase}";
        }
    }
}

