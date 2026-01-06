#!/usr/bin/env python3
"""
Test script to demonstrate the complete authentication flow including refresh tokens
for the Pillio Health Hub API.

Run this script to test:
1. User registration
2. User login
3. Using access token for authenticated requests
4. Token refresh when access token expires
"""

import requests
import json
import time
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

class AuthTester:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.user_email = f"testuser_{int(time.time())}@example.com"
        self.user_password = "SecurePass123!"

    def print_response(self, response, title=""):
        """Pretty print API response"""
        print(f"\n{'='*50}")
        print(f"{title}")
        print(f"{'='*50}")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response: {response.text}")
        print(f"{'='*50}\n")

    def register_user(self):
        """Register a new user"""
        print(f"🔐 Registering user: {self.user_email}")
        
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": self.user_email,
            "password": self.user_password,
            "first_name": "Test",
            "last_name": "User"
        })
        
        self.print_response(response, "USER REGISTRATION")
        
        if response.status_code == 201:
            tokens = response.json()
            self.access_token = tokens['access_token']
            self.refresh_token = tokens['refresh_token']
            print("✅ Registration successful!")
            return True
        else:
            print("❌ Registration failed!")
            return False

    def login_user(self):
        """Login user and get tokens"""
        print(f"🔐 Logging in user: {self.user_email}")
        
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": self.user_email,
            "password": self.user_password
        })
        
        self.print_response(response, "USER LOGIN")
        
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens['access_token']
            self.refresh_token = tokens['refresh_token']
            print("✅ Login successful!")
            return True
        else:
            print("❌ Login failed!")
            return False

    def make_authenticated_request(self, endpoint="/auth/me"):
        """Make an authenticated API request"""
        if not self.access_token:
            print("❌ No access token available!")
            return None
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        print(f"🔒 Making authenticated request to: {endpoint}")
        
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        self.print_response(response, "AUTHENTICATED REQUEST")
        
        return response

    def refresh_access_token(self):
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            print("❌ No refresh token available!")
            return False
            
        print("🔄 Refreshing access token...")
        
        response = requests.post(f"{BASE_URL}/auth/refresh", json={
            "refresh_token": self.refresh_token
        })
        
        self.print_response(response, "TOKEN REFRESH")
        
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens['access_token']
            self.refresh_token = tokens['refresh_token']  # Update refresh token too
            print("✅ Token refresh successful!")
            return True
        else:
            print("❌ Token refresh failed!")
            return False

    def test_expired_token_scenario(self):
        """Simulate scenario where access token is expired"""
        print("🧪 Testing expired token scenario...")
        
        # Make a request that should work
        response1 = self.make_authenticated_request()
        
        # Simulate token expiration by clearing the access token
        print("💭 Simulating token expiration...")
        old_access_token = self.access_token
        self.access_token = "invalid_token"
        
        # This should fail
        response2 = self.make_authenticated_request()
        
        # Restore valid token and refresh
        self.access_token = old_access_token
        print("🔄 Attempting to refresh expired token...")
        
        if self.refresh_access_token():
            print("✅ Successfully handled expired token!")
            # Now this should work again
            self.make_authenticated_request()
        else:
            print("❌ Failed to handle expired token!")

    def run_full_test(self):
        """Run the complete authentication flow test"""
        print("🚀 Starting Pillio API Authentication Test")
        print(f"Test user: {self.user_email}")
        print(f"Password: {self.user_password}")
        
        try:
            # Test registration
            if not self.register_user():
                return
            
            # Test authenticated request
            self.make_authenticated_request()
            
            # Test login (should work with existing user)
            if not self.login_user():
                return
            
            # Test authenticated request after login
            self.make_authenticated_request()
            
            # Test token refresh
            self.refresh_access_token()
            
            # Test authenticated request after refresh
            self.make_authenticated_request()
            
            # Test expired token scenario
            self.test_expired_token_scenario()
            
            print("🎉 All tests completed!")
            
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to API. Make sure the server is running:")
            print("   cd pillio-backend && python -m uvicorn app.main:app --reload")
        except Exception as e:
            print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    tester = AuthTester()
    tester.run_full_test()