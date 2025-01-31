## OBJECTIVE

The reason that this repository exist is to test how to build an API with a Text Generative AI ([Llama-3.2-1B-Instruct](https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct)) using containers, specifically, Podman.

### NEEDED INSTALLATIONS

You need any container engine, here I use podman, but any can be used. If you use podman, you need podman CLI installed. It is available in their website.

### How to run?

You have the option to use containers or just run it locally. To run locally first install the requirements using the next command:

    pip install -r app_files/requirements.txt

Then you can run the API with:

    python app_files/app.py

To use containers, follow the next steps. If you use another container engine, change the podman command to that engine one.

#### 1. Create secret

You need to create a secret with this structure. The token you need to add is the hugging face token that can be generated in their website.

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
