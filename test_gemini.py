import os
import requests
import json

# Get API key from environment variable
api_key = os.environ['GeminiApiKey']

# API endpoint
url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash-001:generateContent?key={api_key}"

# Request headers
headers = {
    "Content-Type": "application/json"
}

# Request body
data = {
    "contents": [
        {
            "parts": [
                {
                    "text": "こんにちは"
                }
            ]
        }
    ]
}

# Make the API request
response = requests.post(url, headers=headers, json=data)

# Print the response
print(json.dumps(response.json(), indent=2, ensure_ascii=False)) 