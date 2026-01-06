from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import logging
from app.config import settings
from app.schemas.common import TokenData

logger = logging.getLogger(__name__)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    try:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        
        logger.debug(f"Created access token for subject: {data.get('sub')}")
        return encoded_jwt
        
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    try:
        to_encode = data.copy()
        
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        
        logger.debug(f"Created refresh token for subject: {data.get('sub')}")
        return encoded_jwt
        
    except Exception as e:
        logger.error(f"Error creating refresh token: {e}")
        raise


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
                logger.warning(f"Token type mismatch: expected refresh, got {token_subtype}")
                return None
        elif token_type == "access":
            # Access tokens don't have a type field, but refresh tokens do
            if payload.get("type") == "refresh":
                logger.warning("Token type mismatch: access token has refresh type")
                return None
        
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if email is None or user_id is None:
            logger.warning("Token missing required fields (sub or user_id)")
            return None
        
        logger.debug(f"Token verified successfully for user: {email}")
        return TokenData(email=email, user_id=user_id)
        
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        return None


def verify_access_token(token: str) -> Optional[TokenData]:
    """Verify an access token"""
    logger.debug("Verifying access token")
    return verify_token(token, "access")


def verify_refresh_token(token: str) -> Optional[TokenData]:
    """Verify a refresh token"""
    logger.debug("Verifying refresh token")
    return verify_token(token, "refresh")


def get_token_expiration(token: str) -> Optional[datetime]:
    """Get the expiration time of a token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        exp_timestamp = payload.get("exp")
        
        if exp_timestamp is None:
            logger.warning("Token has no expiration field")
            return None
        
        expiration = datetime.utcfromtimestamp(exp_timestamp)
        logger.debug(f"Token expiration: {expiration}")
        return expiration
        
    except JWTError as e:
        logger.warning(f"Failed to decode token for expiration: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting token expiration: {e}")
        return None


def is_token_expired(token: str) -> bool:
    """Check if a token is expired"""
    try:
        expiration = get_token_expiration(token)
        if expiration is None:
            return True
        
        is_expired = datetime.utcnow() >= expiration
        if is_expired:
            logger.debug("Token is expired")
        else:
            logger.debug("Token is still valid")
        
        return is_expired
        
    except Exception as e:
        logger.error(f"Error checking token expiration: {e}")
        return True


def decode_token_without_verification(token: str) -> Optional[dict]:
    """Decode a token without signature verification (for debugging only)"""
    try:
        # This is for debugging purposes only - DO NOT use in production
        payload = jwt.decode(token, options={"verify_signature": False})
        logger.warning("Token decoded without verification (debug only)")
        return payload
        
    except JWTError as e:
        logger.warning(f"Failed to decode token without verification: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {e}")
        return None
