from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings
from app.schemas.common import TokenData


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
    """
    Verify a JWT token and return the token data
    
    Args:
        token: The JWT token to verify
        token_type: Type of token ("access" or "refresh")
    
    Returns:
        TokenData object if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Check token type
        if token_type == "refresh":
            token_subtype = payload.get("type")
            if token_subtype != "refresh":
                return None
        elif token_type == "access":
            # Access tokens don't have a type field, but refresh tokens do
            if payload.get("type") == "refresh":
                return None
        
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if email is None or user_id is None:
            return None
        
        return TokenData(email=email, user_id=user_id)
    
    except JWTError:
        return None


def verify_access_token(token: str) -> Optional[TokenData]:
    """Verify an access token"""
    return verify_token(token, "access")


def verify_refresh_token(token: str) -> Optional[TokenData]:
    """Verify a refresh token"""
    return verify_token(token, "refresh")


def get_token_expiration(token: str) -> Optional[datetime]:
    """Get the expiration time of a token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        exp_timestamp = payload.get("exp")
        
        if exp_timestamp is None:
            return None
        
        return datetime.utcfromtimestamp(exp_timestamp)
    
    except JWTError:
        return None


def is_token_expired(token: str) -> bool:
    """Check if a token is expired"""
    expiration = get_token_expiration(token)
    if expiration is None:
        return True
    
    return datetime.utcnow() >= expiration


def decode_token_without_verification(token: str) -> Optional[dict]:
    """Decode a token without signature verification (for debugging only)"""
    try:
        # This is for debugging purposes only - DO NOT use in production
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except JWTError:
        return None