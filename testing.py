import requests

url = "https://opwebhook.onrender.com/webhook"
data = {
    "action": "Жопа",
    "message": "вика привет"
}

response = requests.post(url, json=data)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
