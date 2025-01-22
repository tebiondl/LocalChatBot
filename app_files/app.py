from flask import Flask, request, jsonify
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import os
import torch
from dotenv import load_dotenv
import json

load_dotenv()

# Load env variables
if os.path.exists(os.getenv("LOCAL_SECRETS_PATH")):
    secrets_path = os.getenv("LOCAL_SECRETS_PATH")
else:
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
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.bfloat16 if device == "cuda" else torch.float32
    )
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer, 
        device=0 if device == "cuda" else -1,
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
    
        outputs = pipe(prompt, num_return_sequences=1)
        generated_text = outputs[0]["generated_text"]
            
        return jsonify({"generated_text": generated_text})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


'''
Request Type: POST
Input Data: {"*": "Any existant parameter for an specific model configuration"}
Output Data: {"A good message if the configuration was applied"}
'''
@app.route("/change_config", methods=["POST"])
def change_config():
    global pipe, model, tokenizer
    try:
        # Get data from the request
        data = request.get_json()

        # It checks if the model config has this specific configutrations
        for key, value in data.items():
            if hasattr(model.config, key):
                setattr(model.config, key, value)
            else:
                raise ValueError(f"Invalid config key: {key}")
            
        # Refresh pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer, 
            device=0 if device == "cuda" else -1,
            token=hf_token
        )
            
        return jsonify("Applied Configuration")
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
