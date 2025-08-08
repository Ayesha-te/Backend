#!/usr/bin/env python
import requests
import json

# Test admin API endpoints
BASE_URL = 'http://127.0.0.1:8000/api'

def test_endpoint(endpoint, method='GET', data=None):
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*50}")
    print(f"Testing: {method} {url}")
    print('='*50)
    
    try:
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict) and 'results' in result:
                print(f"Results count: {len(result['results'])}")
                if result['results']:
                    print("Sample result:")
                    print(json.dumps(result['results'][0], indent=2))
            else:
                print("Response:")
                print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

def main():
    print("Testing Admin API Endpoints")
    print("="*50)
    
    # Test users endpoint
    test_endpoint('/users/')
    
    # Test bookings endpoint
    test_endpoint('/bookings/')
    
    # Test services endpoint
    test_endpoint('/services/')
    
    # Test counts
    test_endpoint('/users/count/')
    test_endpoint('/bookings/count/')
    test_endpoint('/payments/total/')
    
    # Test creating a user
    user_data = {
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'testpass123',
        'is_active': True,
        'is_staff': False
    }
    test_endpoint('/users/', 'POST', user_data)

if __name__ == '__main__':
    main()