import os

def __init__(self):
    self.api_key = os.getenv("HF_API_KEY")

    if not self.api_key or not self.api_key.startswith("hf_"):
        print("⚠️  No valid Hugging Face API key found. Falling back to local letters.")
        self.use_api = False
    else:
        self.use_api = True

        self.api_url = "https://router.huggingface.co/hf-inference/models/mistralai/Mistral-7B-Instruct-v0.2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
}


        print("✅ Hugging Face API initialized")
        print("🔗 Model:", self.api_url)
