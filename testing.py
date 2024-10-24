import requests

url = "https://opwebhook.onrender.com/webhook"
data = {
    "action": "test_event",
    "message": "This is a test notification"
}

response = requests.post(url, json=data)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
