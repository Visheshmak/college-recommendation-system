"""
Validation and Security Utilities
Provides input validation, sanitization, and security checks
"""

import re
from typing import Optional, Dict, Any
from functools import wraps
from flask import request, abort, jsonify
from datetime import datetime, timedelta
import json

# Rate limiting dictionary (in production, use Redis)
rate_limit_store = {}


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_percentile(percentile: float) -> bool:
    """
    Validate exam percentile (0-100).
    
    Args:
        percentile (float): Percentile to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        p = float(percentile)
        return 0 <= p <= 100
    except (ValueError, TypeError):
        return False


def validate_required_fields(data: Dict, required_fields: list) -> bool:
    """
    Validate that all required fields are present and non-empty.
    
    Args:
        data (Dict): Data dictionary to validate
        required_fields (list): List of required field names
        
    Returns:
        bool: True if all required fields present and non-empty
        
    Raises:
        ValidationError: If required fields are missing
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
    
    return True


def sanitize_string(text: str, max_length: int = 500) -> str:
    """
    Sanitize string input to prevent injection attacks.
    
    Args:
        text (str): String to sanitize
        max_length (int): Maximum allowed length
        
    Returns:
        str: Sanitized string
        
    Raises:
        ValidationError: If string exceeds max length
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Check length
    if len(text) > max_length:
        raise ValidationError(f"Input exceeds maximum length of {max_length} characters")
    
    # Remove potentially dangerous characters
    dangerous_chars = r'[<>\"\'%;()&+]'
    text = re.sub(dangerous_chars, '', text)
    
    return text


def validate_search_query(query: str) -> str:
    """
    Validate and sanitize search query.
    
    Args:
        query (str): Search query to validate
        
    Returns:
        str: Sanitized query
        
    Raises:
        ValidationError: If query is invalid
    """
    if not query or not isinstance(query, str):
        raise ValidationError("Search query must be a non-empty string")
    
    query = sanitize_string(query, max_length=200)
    
    if len(query) < 2:
        raise ValidationError("Search query must be at least 2 characters")
    
    return query


def validate_college_filters(filters: Dict) -> Dict:
    """
    Validate college filter parameters.
    
    Args:
        filters (Dict): Dictionary of filters to validate
        
    Returns:
        Dict: Validated filters
        
    Raises:
        ValidationError: If filters are invalid
    """
    validated = {}
    
    # Validate city
    if 'city' in filters:
        validated['city'] = sanitize_string(filters['city'], max_length=50)
    
    # Validate branch
    if 'branch' in filters:
        valid_branches = ['CSE', 'ECE', 'EE', 'ME', 'CE', 'ChE', 'IT', 'Biomedical']
        branch = filters['branch'].upper()
        if branch not in valid_branches:
            raise ValidationError(f"Invalid branch: {branch}")
        validated['branch'] = branch
    
    # Validate category
    if 'category' in filters:
        valid_categories = ['General', 'OBC', 'SC', 'ST', 'PWD']
        category = filters['category']
        if category not in valid_categories:
            raise ValidationError(f"Invalid category: {category}")
        validated['category'] = category
    
    # Validate fees range
    if 'fees_min' in filters or 'fees_max' in filters:
        try:
            if 'fees_min' in filters:
                fees_min = float(filters['fees_min'])
                if fees_min < 0:
                    raise ValidationError("Fees minimum cannot be negative")
                validated['fees_min'] = fees_min
            
            if 'fees_max' in filters:
                fees_max = float(filters['fees_max'])
                if fees_max < 0:
                    raise ValidationError("Fees maximum cannot be negative")
                validated['fees_max'] = fees_max
            
            if 'fees_min' in validated and 'fees_max' in validated:
                if validated['fees_min'] > validated['fees_max']:
                    raise ValidationError("Fees minimum cannot be greater than maximum")
        except ValueError:
            raise ValidationError("Fees must be numeric values")
    
    # Validate rating
    if 'rating_min' in filters:
        try:
            rating = float(filters['rating_min'])
            if not (0 <= rating <= 5):
                raise ValidationError("Rating must be between 0 and 5")
            validated['rating_min'] = rating
        except ValueError:
            raise ValidationError("Rating must be a numeric value")
    
    return validated


def rate_limit(max_requests: int = 100, time_window: int = 3600):
    """
    Decorator for rate limiting API endpoints.
    
    Args:
        max_requests (int): Maximum requests allowed in time window
        time_window (int): Time window in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client IP
            client_ip = request.remote_addr
            current_time = datetime.now()
            
            # Initialize if first request
            if client_ip not in rate_limit_store:
                rate_limit_store[client_ip] = {'requests': [], 'blocked_until': None}
            
            client_data = rate_limit_store[client_ip]
            
            # Check if client is temporarily blocked
            if client_data['blocked_until']:
                if datetime.now() < client_data['blocked_until']:
                    return jsonify({'error': 'Rate limit exceeded. Try again later.'}), 429
                else:
                    client_data['blocked_until'] = None
                    client_data['requests'] = []
            
            # Remove old requests outside time window
            client_data['requests'] = [
                req_time for req_time in client_data['requests']
                if (current_time - req_time).total_seconds() < time_window
            ]
            
            # Check request limit
            if len(client_data['requests']) >= max_requests:
                # Block for 1 hour
                client_data['blocked_until'] = current_time + timedelta(hours=1)
                return jsonify({'error': 'Rate limit exceeded. Try again later.'}), 429
            
            # Record this request
            client_data['requests'].append(current_time)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_password(password: str, min_length: int = 8) -> bool:
    """
    Validate password strength.
    
    Args:
        password (str): Password to validate
        min_length (int): Minimum password length
        
    Returns:
        bool: True if password meets requirements
        
    Raises:
        ValidationError: If password is weak
    """
    if len(password) < min_length:
        raise ValidationError(f"Password must be at least {min_length} characters")
    
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain lowercase letters")
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain uppercase letters")
    
    if not re.search(r'[0-9]', password):
        raise ValidationError("Password must contain numbers")
    
    return True


def validate_username(username: str) -> bool:
    """
    Validate username format.
    
    Args:
        username (str): Username to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If username is invalid
    """
    if len(username) < 4:
        raise ValidationError("Username must be at least 4 characters")
    
    if len(username) > 20:
        raise ValidationError("Username must not exceed 20 characters")
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        raise ValidationError("Username can only contain letters, numbers, underscores, and hyphens")
    
    return True


def format_error_response(error_msg: str, error_code: str = None) -> Dict:
    """
    Format error response for API.
    
    Args:
        error_msg (str): Error message
        error_code (str): Optional error code
        
    Returns:
        Dict: Formatted error response
    """
    return {
        'success': False,
        'error': error_msg,
        'error_code': error_code,
        'timestamp': datetime.now().isoformat()
    }


def format_success_response(data: Any, message: str = "Success") -> Dict:
    """
    Format success response for API.
    
    Args:
        data (Any): Response data
        message (str): Success message
        
    Returns:
        Dict: Formatted success response
    """
    return {
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }
