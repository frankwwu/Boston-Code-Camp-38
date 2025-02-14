using DotNetEnv;
using System.Text;
using System.Text.Json;

namespace DeepSeek_Together_AI
{
    class Program
    {
        private static string apiKey = string.Empty;
        private static string model = string.Empty;

        static async Task Main()
        {
            Env.Load();
            apiKey = Env.GetString("TOGETHER_AI_KEY");
            model = "deepseek-ai/DeepSeek-R1";

            while (true)
            {
                Console.Write("\nQuestion: ");

                var prompt = Console.ReadLine();
                if (string.IsNullOrWhiteSpace(prompt))
                {
                    break;
                }

                string response = await GetTogetherAIResponse(prompt);
                Console.WriteLine(response);
                Console.WriteLine();
            }
        }

        static async Task<string> GetTogetherAIResponse(string prompt)
        {
            using HttpClient client = new HttpClient();
            client.DefaultRequestHeaders.Add("Authorization", $"Bearer {apiKey}");

            var requestBody = new
            {
                model = model,
                prompt = prompt,
                max_tokens = 1200,
                temperature = 0.25
            };

            string jsonBody = JsonSerializer.Serialize(requestBody);
            var content = new StringContent(jsonBody, Encoding.UTF8, "application/json");

            HttpResponseMessage response = await client.PostAsync("https://api.together.ai/v1/completions", content);
            if (response.IsSuccessStatusCode)
            {
                string responseString = await response.Content.ReadAsStringAsync();
                using JsonDocument doc = JsonDocument.Parse(responseString);
                JsonElement root = doc.RootElement;

                if (root.TryGetProperty("choices", out JsonElement choices) && choices.GetArrayLength() > 0)
                {
                    return choices[0].GetProperty("text").GetString() ?? "No response received.";
                }
            }

            return $"Error: {response.StatusCode} - {response.ReasonPhrase}";
        }
    }
}

