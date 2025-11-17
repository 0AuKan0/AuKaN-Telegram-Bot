import requests
import os

API_KEY = os.environ.get('DEEPSEEK_API_KEY')

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

data = {
    'model': 'deepseek-chat',
    'messages': [{'role': 'user', 'content': 'Hola, responde con OK si funciona'}]
}

response = requests.post('https://api.deepseek.com/chat/completions', json=data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
