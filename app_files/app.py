from flask import Flask, request, jsonify
from transformers import pipeline
import os
import torch
from dotenv import load_dotenv
import json

load_dotenv()

# Load env variables
secrets_path = os.getenv("SECRETS_PATH")
try:
    with open(secrets_path, "r") as f:
        secrets = json.load(f)
except FileNotFoundError:
    raise ValueError("Secrets file not configured")
except json.JSONDecodeError:
    raise ValueError("Secrets file has not a valid JSON")

hf_token = secrets["hf_token"]
if not hf_token:
    raise ValueError("There is no huggingface token in the secrets")

model_id = os.getenv("MODEL_ID")

try:
    # Load model
    pipe = pipeline(
        "text-generation",
        model=model_id,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        device_map="auto",
        token=hf_token
        )
except Exception as e:
    raise RuntimeError(f"Error loading the model: {e}")

# Start flask app
app = Flask(__name__)

'''
Request Type: POST
Input Data: {"prompt": "prompt for the generative model"}
Output Data: {"generated_text": "answer of the model"}
'''
@app.route("/generate", methods=["POST"])
def generate_text():
    try:
        # Get data from the request
        data = request.get_json()
        if not data or "prompt" not in data:
            return jsonify({"error": "Invalid request, 'prompt' is required"}), 400
        
        prompt = data["prompt"]
        if not isinstance(prompt, str) or not prompt.strip():
            return jsonify({"error": "Prompt must be a non-empty string"}), 400
    
        outputs = pipe(prompt, max_new_tokens=256, num_return_sequences=1)
        generated_text = outputs[0]["generated_text"]
            
        return jsonify({"generated_text": generated_text})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
