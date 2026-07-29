"""
Phase 2 Authentication and RBAC Integration Tests

Tests for:
- JWT token validation
- RBAC tier checking
- Customer segment authorization
- Protected endpoint access
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import jwt
import sys
import os
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from middleware import (
    decode_jwt,
    get_current_user,
    create_jwt_token,
    require_auth,
    require_tier,
    require_segment,
    AuthUser,
)


class TestJWTValidation:
    """Test JWT token validation"""
    
    @pytest.mark.asyncio
    async def test_valid_jwt_accepted(self):
        """Test: Valid JWT token is accepted and decoded"""
        with patch('middleware.JWT_SECRET', 'test-secret'):
            # Create a valid token
            payload = {
                "sub": "user-123",
                "email": "user@example.com",
                "tier": "contractor_pro",
                "segment": "contractor",
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=1),
            }
            
            token = jwt.encode(payload, 'test-secret', algorithm="HS256")
            
            # Decode token
            with patch('middleware.JWT_SECRET', 'test-secret'):
                decoded = decode_jwt(token)
                
                # Assertions
                assert decoded["sub"] == "user-123"
                assert decoded["email"] == "user@example.com"
                assert decoded["tier"] == "contractor_pro"
    
    @pytest.mark.asyncio
    async def test_invalid_jwt_rejected(self):
        """Test: Invalid JWT token is rejected"""
        from fastapi import HTTPException
        
        invalid_token = "invalid.jwt.token"
        
        # Attempt to decode
        with pytest.raises(HTTPException) as exc_info:
            decode_jwt(invalid_token)
        
        # Assertions
        assert exc_info.value.status_code == 401


class TestRBACTierCheck:
    """Test RBAC tier-based access control"""
    
    @pytest.mark.asyncio
    async def test_free_tier_rejects_premium_endpoint(self):
        """Test: Free tier user cannot access premium endpoint"""
        from fastapi import HTTPException, Request
        
        # Create mock request with free tier user
        mock_request = MagicMock(spec=Request)
        mock_request.headers.get.return_value = ""
        
        with patch('middleware.get_current_user', new_callable=AsyncMock) as mock_get_user:
            # Return free tier user
            mock_get_user.return_value = AuthUser(
                user_id="user-123",
                email="user@example.com",
                tier="free",
                segment="contractor"
            )
            
            # Attempt to call premium endpoint
            @require_tier("contractor_pro", "ic_consultant")
            async def premium_endpoint(request):
                return {"message": "premium access"}
            
            with pytest.raises(HTTPException) as exc_info:
                await premium_endpoint(mock_request)
            
            # Assertions
            assert exc_info.value.status_code == 403
    
    @pytest.mark.asyncio
    async def test_pro_tier_accepts_premium_endpoint(self):
        """Test: Pro tier user can access premium endpoint"""
        from fastapi import Request
        
        # Create mock request
        mock_request = MagicMock(spec=Request)
        mock_request.headers.get.return_value = "Bearer token"
        mock_request.state = MagicMock()
        
        with patch('middleware.get_current_user', new_callable=AsyncMock) as mock_get_user:
            # Return pro tier user
            mock_get_user.return_value = AuthUser(
                user_id="user-123",
                email="user@example.com",
                tier="contractor_pro",
                segment="contractor"
            )
            
            # Call premium endpoint
            @require_tier("contractor_pro", "ic_consultant")
            async def premium_endpoint(request):
                return {"message": "premium access"}
            
            result = await premium_endpoint(mock_request)
            
            # Assertions
            assert result["message"] == "premium access"
            assert mock_request.state.user.tier == "contractor_pro"


class TestAuthenticationDecorator:
    """Test @require_auth decorator"""
    
    @pytest.mark.asyncio
    async def test_authenticated_user_allowed(self):
        """Test: Authenticated user can access protected endpoint"""
        from fastapi import Request
        
        mock_request = MagicMock(spec=Request)
        mock_request.state = MagicMock()
        
        with patch('middleware.get_current_user', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = AuthUser(
                user_id="user-123",
                email="user@example.com",
                tier="free",
                segment="contractor"
            )
            
            @require_auth
            async def protected_endpoint(request):
                return {"message": "success"}
            
            result = await protected_endpoint(mock_request)
            
            assert result["message"] == "success"
    
    @pytest.mark.asyncio
    async def test_unauthenticated_user_denied(self):
        """Test: Unauthenticated user cannot access protected endpoint"""
        from fastapi import HTTPException, Request
        
        mock_request = MagicMock(spec=Request)
        
        with patch('middleware.get_current_user', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = None
            
            @require_auth
            async def protected_endpoint(request):
                return {"message": "success"}
            
            with pytest.raises(HTTPException) as exc_info:
                await protected_endpoint(mock_request)
            
            assert exc_info.value.status_code == 401


class TestSegmentAuthorization:
    """Test customer segment authorization"""
    
    @pytest.mark.asyncio
    async def test_sponsor_segment_allowed(self):
        """Test: Sponsor segment user can access sponsor endpoint"""
        from fastapi import Request
        
        mock_request = MagicMock(spec=Request)
        mock_request.state = MagicMock()
        
        with patch('middleware.get_current_user', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = AuthUser(
                user_id="user-123",
                email="user@example.com",
                tier="sponsor_admin",
                segment="sponsor"
            )
            
            @require_segment("sponsor", "admin")
            async def sponsor_endpoint(request):
                return {"message": "sponsor access"}
            
            result = await sponsor_endpoint(mock_request)
            
            assert result["message"] == "sponsor access"
    
    @pytest.mark.asyncio
    async def test_contractor_segment_denied_sponsor_access(self):
        """Test: Contractor cannot access sponsor endpoint"""
        from fastapi import HTTPException, Request
        
        mock_request = MagicMock(spec=Request)
        
        with patch('middleware.get_current_user', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = AuthUser(
                user_id="user-123",
                email="user@example.com",
                tier="contractor_pro",
                segment="contractor"
            )
            
            @require_segment("sponsor", "admin")
            async def sponsor_endpoint(request):
                return {"message": "sponsor access"}
            
            with pytest.raises(HTTPException) as exc_info:
                await sponsor_endpoint(mock_request)
            
            assert exc_info.value.status_code == 403


class TestJWTTokenCreation:
    """Test JWT token creation"""
    
    @pytest.mark.asyncio
    async def test_jwt_token_creation(self):
        """Test: JWT tokens can be created and contain correct claims"""
        with patch('middleware.JWT_SECRET', 'test-secret'):
            token = await create_jwt_token(
                user_id="user-123",
                email="user@example.com",
                tier="contractor_pro",
                segment="contractor"
            )
            
            # Decode and verify
            with patch('middleware.JWT_SECRET', 'test-secret'):
                decoded = jwt.decode(token, 'test-secret', algorithms=["HS256"])
                
                assert decoded["sub"] == "user-123"
                assert decoded["email"] == "user@example.com"
                assert decoded["tier"] == "contractor_pro"
                assert decoded["segment"] == "contractor"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
