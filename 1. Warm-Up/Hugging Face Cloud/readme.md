# Getting started using Hugging Face with the API:

### 1. Create a Hugging Face Account & Get API Key
1. Go to [Hugging Face](https://huggingface.co/).
2. Sign up or log in.
3. Navigate to [Access Tokens](https://huggingface.co/settings/tokens).
4. Click **New Token**, set the role to **"Write" or "Read"**, and copy the key.

### 2. Install Required Python Packages
Install the Hugging Face `huggingface_hub` library:
```bash
pip install huggingface_hub
```

### 3. Set Up the API Client in Python
Use the `InferenceClient` from `huggingface_hub` to interact with models.

#### **Basic Example (Text Generation)**
```python
from huggingface_hub import InferenceClient

api_key = "your_huggingface_api_key"  # Replace with your API key
client = InferenceClient(token=api_key)

response = client.text_generation(
    prompt="Tell me a short science fiction story.",
    model="gpt2",
    max_new_tokens=90
)

print(response)
```

You're all set! 