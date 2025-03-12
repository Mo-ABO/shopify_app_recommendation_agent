from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app  

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    json_response = response.json()
    assert "message" in json_response
    print("Root endpoint test passed.")

def test_auth_token():
    response = client.post("/token", data={"username": "alice", "password": "password"})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "access_token" in data
    print("Auth token test passed.")

def test_recommendation():
    token_response = client.post("/token", data={"username": "alice", "password": "password"})
    token = token_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {"query": "I need a low-cost inventory management solution for a small clothing store"}
    response = client.post("/v1/ai/recom-app", json=payload, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "recommendations" in data
    print("Recommendation endpoint test passed.")

if __name__ == "__main__":
    test_read_root()
    test_auth_token()
    test_recommendation()
    print("All tests passed!")
