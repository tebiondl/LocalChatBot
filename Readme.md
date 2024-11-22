## OBJECTIVE

The reason that this repository exist is to test how podman works and create a container that holds an API with a text generative AI ([Llama-3.2-1B-Instruct](https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct)).

### NEEDED INSTALLATIONS

You need podman CLI installed. It is available in their website.

### How to run?

Follow the next steps

#### 1. Create secret

You need to create a secret with this structure:

    {
        "hf_token": "YOUR_TOKEN"
    }

Then run

    podman secret create chatbot-secrets secrets.json

#### 2. Build image
    podman build -t local-chatbot .

#### 3. Run container
    podman run -d -p 5000:5000 --secret chatbot-secrets local-chatbot

#### 4. Call the api
    curl -X POST http://localhost:5000/generate -H "Content-Type: application/json" -d '{"prompt": "Write a poem about the stars"}'