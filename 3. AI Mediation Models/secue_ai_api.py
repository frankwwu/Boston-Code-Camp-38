from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from together import Together
from dotenv import load_dotenv, find_dotenv
from transformers import pipeline
from huggingface_hub import login
import os
import uvicorn

# Load environment variables
load_dotenv(find_dotenv())

# Initialize FastAPI app
app = FastAPI()

# Initialize TogetherAI client and models
api_key = os.getenv("TOGETHER_API_KEY")
client = Together()
MODELS = {
    "vision": "meta-llama/Llama-Vision-Free",
    "instruct": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    "distill": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"
}

# Authenticate with Hugging Face Hub
login(os.getenv("HUGGING_FACE_TOKEN"))
llama_guard = pipeline("text-classification", model="meta-llama/Llama-Guard-3-1B")

# Pydantic model for request
class PromptRequest(BaseModel):
    prompt: str

# Utility function for content safety check
def check_safety(text: str) -> float:
    '''
    Developers can set thresholds for flagging or blocking content based on these scores. For example:
        If score < 0.5, allow the response.
        If score between 0.5 and 0.75, require human review.
        If score > 0.75, block the response.
    '''
    result = llama_guard(text)
    return result[0]['score']

# Endpoint to generate text
@app.post("/generate")
def generate_text(request: PromptRequest):
    input_score = check_safety(request.prompt)
    if input_score > 0.99:
        return {"response": "Unsafe prompt detected.", "input_score": input_score}

    response = client.chat.completions.create(
        model=MODELS["distill"],
        messages=[{"role": "user", "content": request.prompt}]
    )

    output_score = check_safety(response.choices[0].message.content)
    return {
        "response": response.choices[0].message.content,
        "input_score": input_score,
        "output_score": output_score
    }

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "AI Demo App Running"}

# Main application entry point
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


# uvicorn main:app --reload
# http://127.0.0.1:8000/docs