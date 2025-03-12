import requests

BASE_URL = "http://127.0.0.1:8000"

token_url = f"{BASE_URL}/token"
login_data = {"username": "alice", "password": "password1"}

token_response = requests.post(token_url, data=login_data)
print("Token response:", token_response.json())
access_token = token_response.json().get("access_token")


recommend_url = f"{BASE_URL}/v1/ai/recom-app"
headers = {"Authorization": f"Bearer {access_token}"}
payload = {"query": "I need a low-cost inventory management solution for a small clothing store"}

recommend_response = requests.post(recommend_url, json=payload, headers=headers)
print("Recommendation response:", recommend_response.json())
