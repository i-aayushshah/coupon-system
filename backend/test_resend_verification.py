import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_resend_verification():
    print("Testing Resend Verification Functionality")
    print("=" * 50)

    # Test 1: Try to login with unverified email (should fail with option to resend)
    print("\n1. Testing login with unverified email:")
    login_data = {
        "email": "aayushshah817@gmail.com",
        "password": "password123"
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 2: Try to login with resend_verification flag
    print("\n2. Testing login with resend_verification flag:")
    login_data_with_resend = {
        "email": "aayushshah817@gmail.com",
        "password": "password123",
        "resend_verification": True
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data_with_resend)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 3: Test dedicated resend verification endpoint
    print("\n3. Testing dedicated resend verification endpoint:")
    resend_data = {
        "email": "aayushshah817@gmail.com"
    }

    response = requests.post(f"{BASE_URL}/auth/resend-verification", json=resend_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 4: Test with non-existent email (should not reveal if email exists)
    print("\n4. Testing with non-existent email:")
    resend_data_fake = {
        "email": "nonexistent@example.com"
    }

    response = requests.post(f"{BASE_URL}/auth/resend-verification", json=resend_data_fake)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_resend_verification()
