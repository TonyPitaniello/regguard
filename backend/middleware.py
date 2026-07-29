"""
Authentication and RBAC Middleware
Handles JWT validation and role-based access control
"""

import os
import logging
from functools import wraps
from typing import List, Optional, Any, Callable
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthCredentials

logger = logging.getLogger(__name__)

# JWT configuration
JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")
ALGORITHM = "HS256"

# Try to import jwt - if not available, functions will raise errors
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    jwt = None

# Valid tiers and customer segments
VALID_TIERS = ["free", "contractor_pro", "ic_consultant", "sponsor_admin", "partner_admin"]
VALID_SEGMENTS = ["contractor", "ic_consultant", "sponsor", "partner", "admin"]

security = HTTPBearer(optional=True)


class AuthUser:
    """Authenticated user information"""
    def __init__(self, user_id: str, email: str, tier: str, segment: str):
        self.id = user_id
        self.email = email
        self.tier = tier
        self.segment = segment


def decode_jwt(token: str) -> dict:
    """
    Decode and validate JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    if not JWT_AVAILABLE:
        raise HTTPException(status_code=500, detail="JWT support not available")
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Error decoding JWT: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


async def get_current_user(request: Request) -> Optional[AuthUser]:
    """
    Extract and validate user from request.
    
    Checks Authorization header for Bearer token.
    Returns None if no token present and auth is optional.
    
    Args:
        request: FastAPI request object
    
    Returns:
        AuthUser if authenticated, None otherwise
    """
    auth_header = request.headers.get("Authorization", "")
    
    if not auth_header:
        return None
    
    try:
        scheme, token = auth_header.split(" ")
        if scheme.lower() != "bearer":
            return None
        
        payload = decode_jwt(token)
        
        # Extract user info from JWT
        user_id = payload.get("sub")
        email = payload.get("email")
        tier = payload.get("tier", "free")
        segment = payload.get("segment", "contractor")
        
        if not user_id:
            return None
        
        return AuthUser(user_id=user_id, email=email, tier=tier, segment=segment)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting user: {e}")
        return None


def require_auth(func: Callable) -> Callable:
    """
    Decorator: Require valid JWT authentication.
    
    Usage:
        @require_auth
        async def protected_endpoint(request: Request, ...):
            user = request.state.user
            ...
    
    Args:
        func: Async endpoint function
    
    Returns:
        Decorated function
    """
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        user = await get_current_user(request)
        
        if not user:
            logger.warning("Unauthorized access attempt")
            raise HTTPException(status_code=401, detail="Authentication required")
        
        request.state.user = user
        return await func(request, *args, **kwargs)
    
    return wrapper


def require_tier(*allowed_tiers: str) -> Callable:
    """
    Decorator: Require user to have one of the specified tiers.
    
    Usage:
        @require_tier("contractor_pro", "ic_consultant")
        async def premium_endpoint(request: Request, ...):
            user = request.state.user
            ...
    
    Args:
        allowed_tiers: Variable number of tier strings
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user = await get_current_user(request)
            
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if user.tier not in allowed_tiers:
                logger.warning(
                    f"Insufficient tier: user={user.id} has tier={user.tier}, "
                    f"required={allowed_tiers}"
                )
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            request.state.user = user
            return await func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator


def require_segment(*allowed_segments: str) -> Callable:
    """
    Decorator: Require user to have one of the specified customer segments.
    
    Usage:
        @require_segment("sponsor", "admin")
        async def sponsor_endpoint(request: Request, ...):
            user = request.state.user
            ...
    
    Args:
        allowed_segments: Variable number of segment strings
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user = await get_current_user(request)
            
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if user.segment not in allowed_segments:
                logger.warning(
                    f"Insufficient segment: user={user.id} has segment={user.segment}, "
                    f"required={allowed_segments}"
                )
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            request.state.user = user
            return await func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator


async def create_jwt_token(
    user_id: str,
    email: str,
    tier: str = "free",
    segment: str = "contractor",
    expires_in: int = 86400,  # 24 hours
) -> str:
    """
    Create a JWT token for a user.
    
    Args:
        user_id: UUID of user
        email: User email
        tier: User tier
        segment: Customer segment
        expires_in: Token lifetime in seconds
    
    Returns:
        JWT token string
    """
    if not JWT_AVAILABLE:
        raise ValueError("JWT support not available")
    
    from datetime import datetime, timedelta
    
    now = datetime.utcnow()
    exp = now + timedelta(seconds=expires_in)
    
    payload = {
        "sub": user_id,
        "email": email,
        "tier": tier,
        "segment": segment,
        "iat": now,
        "exp": exp,
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
    return token


class AuthenticationMiddleware:
    """
    ASGI middleware for extracting user from JWT and attaching to request.state
    """
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Create a fake request object to extract user
        class FakeRequest:
            def __init__(self, scope):
                self.headers = dict(scope.get("headers", []))
        
        fake_request = FakeRequest(scope)
        user = await get_current_user(fake_request)
        
        # Store user in scope for access in endpoints
        scope["user"] = user
        
        await self.app(scope, receive, send)
