"""
Input validation utilities for security.
Prevents SQL injection, XSS, and validates input formats.
"""
import re
import html
from typing import Any, Dict, List
from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException, status

# SQL injection patterns to detect
SQL_INJECTION_PATTERNS = [
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|SCRIPT)\b)",
    r"(--|\/\*|\*\/|;|'|\")",
    r"(\bOR\s+\d+\s*=\s*\d+|\bAND\s+\d+\s*=\s*\d+)",
    r"(\b(WAITFOR|SLEEP|BENCHMARK)\b)",
    r"(@@|INFORMATION_SCHEMA|SYSOBJECTS|SYSCOLUMNS)"
]

def sanitize_string(input_string: str, max_length: int = 255) -> str:
    """
    Sanitize string input to prevent XSS and injection attacks.
    
    Args:
        input_string: The string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
        
    Raises:
        HTTPException: If input contains suspicious patterns
    """
    if not isinstance(input_string, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input must be a string"
        )
    
    if len(input_string) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Input too long. Maximum length: {max_length}"
        )
    
    # Check for SQL injection patterns
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, input_string, re.IGNORECASE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Potentially malicious input detected"
            )
    
    # HTML escape to prevent XSS
    sanitized = html.escape(input_string)
    
    # Remove any remaining potentially dangerous characters
    sanitized = re.sub(r'[<>"\\'`]', '', sanitized)
    
    return sanitized.strip()

def validate_email_format(email: str) -> str:
    """
    Validate email format using comprehensive validation.
    
    Args:
        email: Email address to validate
        
    Returns:
        Validated and normalized email
        
    Raises:
        HTTPException: If email format is invalid
    """
    try:
        # Use email-validator library for comprehensive validation
        valid_email = validate_email(email)
        return valid_email.email.lower()
    except EmailNotValidError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid email format: {str(e)}"
        )

def validate_password_strength(password: str) -> str:
    """
    Validate password strength according to security best practices.
    
    Args:
        password: Password to validate
        
    Returns:
        Valid password
        
    Raises:
        HTTPException: If password doesn't meet requirements
    """
    if not isinstance(password, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be a string"
        )
    
    errors = []
    
    # Length check
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if len(password) > 128:
        errors.append("Password cannot be longer than 128 characters")
    
    # Character type checks
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\\d', password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    # Common weak passwords
    weak_passwords = [
        "password", "123456", "123456789", "qwerty", "abc123",
        "password123", "admin", "letmein", "welcome", "monkey"
    ]
    
    if password.lower() in weak_passwords:
        errors.append("Password is too common and weak")
    
    # Check for sequential characters
    if re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde)', password.lower()):
        errors.append("Password should not contain sequential characters")
    
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"password_errors": errors}
        )
    
    return password

def validate_name(name: str, field_name: str = "name") -> str:
    """
    Validate name fields (full_name, etc.).
    
    Args:
        name: Name to validate
        field_name: Name of the field for error messages
        
    Returns:
        Validated name
        
    Raises:
        HTTPException: If name format is invalid
    """
    if not name:
        return name
    
    # Sanitize the name
    sanitized_name = sanitize_string(name, max_length=100)
    
    # Names should only contain letters, spaces, hyphens, and apostrophes
    if not re.match(r"^[a-zA-ZÀ-ÿ\s\-\']+$", sanitized_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} can only contain letters, spaces, hyphens, and apostrophes"
        )
    
    # Check length
    if len(sanitized_name) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} cannot be longer than 100 characters"
        )
    
    return sanitized_name

def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively sanitize all string values in a dictionary.
    
    Args:
        data: Dictionary to sanitize
        
    Returns:
        Dictionary with sanitized string values
    """
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            # Don't over-sanitize email and password fields during registration
            if key.lower() in ['password', 'email']:
                sanitized[key] = value
            else:
                sanitized[key] = sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_string(item) if isinstance(item, str) else item for item in value]
        else:
            sanitized[key] = value
    
    return sanitized

def validate_json_payload(data: Dict[str, Any], max_keys: int = 50) -> Dict[str, Any]:
    """
    Validate JSON payload for security issues.
    
    Args:
        data: JSON data to validate
        max_keys: Maximum number of keys allowed
        
    Returns:
        Validated data
        
    Raises:
        HTTPException: If payload has security issues
    """
    if not isinstance(data, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload must be a JSON object"
        )
    
    if len(data) > max_keys:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many keys in payload. Maximum: {max_keys}"
        )
    
    return sanitize_dict(data)

# Common regex patterns
PATTERNS = {
    'alphanumeric': re.compile(r'^[a-zA-Z0-9]+$'),
    'alpha_space': re.compile(r'^[a-zA-Z\s]+$'),
    'numeric': re.compile(r'^[0-9]+$'),
    'phone': re.compile(r'^[\+]?[1-9]?[0-9]{7,15}$'),
    'url': re.compile(
        r'^https?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+' # domain...
        r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # host...
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
}

def validate_pattern(value: str, pattern_name: str, field_name: str = "field") -> str:
    """
    Validate string against predefined patterns.
    
    Args:
        value: Value to validate
        pattern_name: Name of the pattern to use
        field_name: Name of the field for error messages
        
    Returns:
        Validated value
        
    Raises:
        HTTPException: If value doesn't match pattern
    """
    if pattern_name not in PATTERNS:
        raise ValueError(f"Unknown pattern: {pattern_name}")
    
    if not PATTERNS[pattern_name].match(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} format is invalid"
        )
    
    return value
