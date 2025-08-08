#!/usr/bin/env python3
"""
Test script for Admin API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_endpoint(endpoint, method="GET", data=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        elif method == "PUT":
            response = requests.put(url, json=data, headers={'Content-Type': 'application/json'})
        elif method == "DELETE":
            response = requests.delete(url)
        
        print(f"\n{method} {endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)[:500]}...")
            except:
                print(f"Response: {response.text[:200]}...")
        else:
            print(f"Error: {response.text}")
            
        return response
        
    except Exception as e:
        print(f"Error testing {endpoint}: {e}")
        return None

def main():
    """Test all admin API endpoints"""
    print("Testing Admin API Endpoints")
    print("=" * 50)
    
    # Test basic endpoints
    endpoints = [
        "/users/count/",
        "/bookings/count/",
        "/payments/total/",
        "/services/",
        "/bookings/",
        "/users/",
        "/bookings/trends/",
        "/bookings/service-distribution/"
    ]
    
    for endpoint in endpoints:
        test_endpoint(endpoint)
    
    print("\n" + "=" * 50)
    print("API Testing Complete")

if __name__ == "__main__":
    main()