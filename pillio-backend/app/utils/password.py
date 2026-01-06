from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
import secrets

# Password hashing using Argon2
ph = PasswordHasher()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except (VerifyMismatchError, InvalidHash):
        return False


def get_password_hash(password: str) -> str:
    """Hash a password for storing"""
    return ph.hash(password)


def create_password_reset_token(email: str) -> str:
    """Create a password reset token"""
    from jose import JWTError, jwt
    from datetime import datetime, timedelta
    from app.config import settings
    
    expire = datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
    to_encode = {"exp": expire, "sub": email, "type": "password_reset"}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    """Verify a password reset token and return email"""
    from jose import JWTError, jwt
    from app.config import settings
    
    try:
        decoded_token = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = decoded_token.get("sub")
        token_type: str = decoded_token.get("type")
        
        if email and token_type == "password_reset":
            return email
    except JWTError:
        return None
    return None


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength
    Returns (is_valid, list_of_errors)
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if len(password) > 128:
        errors.append("Password must be less than 128 characters")
    
    if not any(char.isupper() for char in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(char.islower() for char in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(char.isdigit() for char in password):
        errors.append("Password must contain at least one number")
    
    if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in password):
        errors.append("Password must contain at least one special character")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token"""
    return secrets.token_urlsafe(length)