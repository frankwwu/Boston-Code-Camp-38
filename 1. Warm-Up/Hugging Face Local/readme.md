# Get started using Hugging Face:

1. Create an Account at [https://huggingface.co](https://huggingface.co).

2. Select **Settings** from the dropdown menu, find and click **Access Tokens**, Click **New Token**, then follow the instruction to create and copy the new token.

2. Install the required libraries. For example:
     ```bash
     pip install huggingface_hub 
     pip install transformers
     ```
3. Find models at  [https://huggingface.co/models](https://huggingface.co/models)

4. Use a Pre-trained Model. For example, to generate text with GPT-J 6B:
     ```python
     from transformers import pipeline

     # Create a text generation pipeline with a pre-trained model
     generator = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B')
     
     # Generate text based on a prompt
     prompt = "How big is Greenland?"
     results = generator(prompt, max_length=50)
     
     # Print the generated text
     print(results[0]['generated_text'])
     ```
By following these steps, you can quickly begin using Hugging Face’s powerful tools to build and deploy machine learning models in your projects. For more detailed guides and advanced usage, check out the [official Hugging Face documentation](https://huggingface.co/docs).