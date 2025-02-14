# Get started with Together AI

1. Create an Account at [https://together.ai/](https://together.ai/) 
  
2. Get Your API Key at [https://api.together.ai/settings/api-keys](https://api.together.ai/settings/api-keys)

3. Install the required libraries. For example:
     ```bash
     pip install together-ai
     ```

4. Find models at  [https://api.together.xyz/models](https://api.together.xyz/models)

5. Integrate Together AI into Your Code 
   Here’s a simple Python example assuming a client library is available:
     ```python
     import together_ai

     # Initialize the client with your API key
     client = together_ai.Client(api_key="YOUR_API_KEY")

     # Make an API call (example: generating a chat completion)
     response = client.chat.completions.create(
         model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",  # Replace with the specific model name
         messages=[{"role": "user", "content": "How big is Greenland?"}]
     )

     # Extract and print the generated message
     response_text = response.choices[0].message.content
     print(response_text)
     ```

By following these steps, you should be able to quickly get started using Together AI in your projects. If you run into any issues or have questions, checking the official documentation or support forums is a good next step.