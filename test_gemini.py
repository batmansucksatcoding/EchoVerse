import requests

api_key = 'AIzaSyBy_5otZKwGKqw5WC5seTcTcEDq1TzwV84'

# List available models
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)

print("Status Code:", response.status_code)
print("\nAvailable Models:")
print(response.text)

if response.status_code == 200:
    data = response.json()
    if "models" in data:
        for model in data["models"]:
            if "generateContent" in model.get("supportedGenerationMethods", []):
                print(f"✅ {model['name']}")