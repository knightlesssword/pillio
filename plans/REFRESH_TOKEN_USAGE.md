# Refresh Token Usage Guide

This guide explains how the refresh token system works in the Pillio Health Hub API and how to use it properly.

## Overview

The API uses a two-token system for authentication:
1. **Access Token**: Short-lived token (default: 30 minutes) used for API requests
2. **Refresh Token**: Long-lived token (default: 7 days) used to get new access tokens

## Token Generation

Both tokens are generated automatically when a user:
- Registers: `POST /api/v1/auth/register`
- Logs in: `POST /api/v1/auth/login`

### Response Example
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## Using the Refresh Token

### Step 1: Make API requests with access token
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     http://localhost:8000/api/v1/auth/me
```

### Step 2: When access token expires, use refresh token
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
     -H "Content-Type: application/json" \
     -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

### Step 3: Use the new access token
The refresh endpoint returns a new access token and refresh token:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## Complete Authentication Flow

### 1. User Registration/Login
```python
import requests

# Register a new user
response = requests.post('http://localhost:8000/api/v1/auth/register', json={
    "email": "user@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
})

tokens = response.json()
access_token = tokens['access_token']
refresh_token = tokens['refresh_token']
```

### 2. Use Access Token for API Calls
```python
# Make authenticated API requests
headers = {'Authorization': f'Bearer {access_token}'}
response = requests.get('http://localhost:8000/api/v1/auth/me', headers=headers)
user_data = response.json()
```

### 3. Refresh Token When Needed
```python
# Check if token is expired and refresh if needed
def is_token_expired(response):
    return response.status_code == 401

# When you get a 401, refresh the token
if is_token_expired(response):
    refresh_response = requests.post('http://localhost:8000/api/v1/auth/refresh', json={
        "refresh_token": refresh_token
    })
    
    if refresh_response.status_code == 200:
        new_tokens = refresh_response.json()
        access_token = new_tokens['access_token']
        refresh_token = new_tokens['refresh_token']  # Update refresh token too
        headers = {'Authorization': f'Bearer {access_token}'}
        # Retry the original request
        response = requests.get('http://localhost:8000/api/v1/auth/me', headers=headers)
```

## Token Expiration Times

- **Access Token**: 30 minutes (configurable via `access_token_expire_minutes`)
- **Refresh Token**: 7 days (configurable via `refresh_token_expire_days`)

## Security Best Practices

1. **Store tokens securely**: Use secure storage mechanisms (not localStorage for web apps)
2. **Update refresh token**: Always use the new refresh token returned by the refresh endpoint
3. **Handle token expiration**: Check for 401 responses and automatically refresh tokens
4. **Logout properly**: Clear stored tokens on logout
5. **HTTPS in production**: Always use HTTPS in production to protect tokens in transit

## Error Responses

### Invalid Refresh Token (401)
```json
{
  "detail": "Invalid refresh token"
}
```

### Expired Refresh Token (401)
```json
{
  "detail": "Invalid refresh token"
}
```

## Configuration

Token expiration times can be configured in `app/config.py`:

```python
# Security
access_token_expire_minutes: int = 30
refresh_token_expire_days: int = 7
```

## Implementation Tips

1. **Automatic refresh**: Implement automatic token refresh before making API calls
2. **Token validation**: Consider validating tokens before making requests
3. **Error handling**: Handle network errors and token refresh failures gracefully
4. **User experience**: Provide smooth user experience without requiring manual re-login