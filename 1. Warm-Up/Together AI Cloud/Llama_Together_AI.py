import os
import requests
import json

def load_env():
    from dotenv import load_dotenv
    load_dotenv()

def get_together_ai_response(api_key, model, chat_history):
    url = "https://api.together.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    messages = [{"role": item[0], "content": item[1]} for item in chat_history]

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 1200,
        "temperature": 0.25
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        response_json = response.json()
        choices = response_json.get("choices", [])
        if choices:
            return choices[0]["message"]["content"]
        return "No response received."
    else:
        return f"Error: {response.status_code} - {response.reason}" 


def main():
    load_env()
    api_key = os.getenv("TOGETHER_AI_KEY")
    model = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
    chat_history = []

    while True:
        prompt = input("\nQuestion: ")
        if not prompt.strip():
            break

        chat_history.append(("user", prompt))
        response = get_together_ai_response(api_key, model, chat_history)

        print(response)

        chat_history.append(("assistant", response))


if __name__ == "__main__":
    main()
