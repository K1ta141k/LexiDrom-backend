"""
Authentication API routes
Handles Google OAuth authentication
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from app.models.schemas import GoogleLoginRequest, Token, User
from app.core.auth import verify_google_token, create_access_token, get_google_oauth_url, get_current_user
from app.services.activity_tracker import ActivityTracker
from typing import Optional

router = APIRouter()

# Global tracker (will be set by main.py)
tracker: Optional[ActivityTracker] = None

@router.get("/google-url")
async def get_google_auth_url():
    """Get Google OAuth URL"""
    try:
        auth_url = get_google_oauth_url()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate auth URL: {str(e)}")

@router.post("/google-login", response_model=Token)
async def google_login(request: GoogleLoginRequest, http_req: Request):
    """Login with Google ID token"""
    try:
        print(f"🔍 Attempting Google login with token length: {len(request.id_token) if request.id_token else 0}")
        
        # Verify Google token
        user_info = await verify_google_token(request.id_token)
        if not user_info:
            print("❌ Google token verification failed")
            raise HTTPException(status_code=401, detail="Invalid Google token")
        
        print(f"✅ Google token verified for user: {user_info['email']}")
        
        # Extract user information
        user_email = user_info["email"]
        user_name = user_info.get("name")
        user_picture = user_info.get("picture")
        
        # Create access token
        access_token_expires = None  # Use default from settings
        access_token = create_access_token(
            data={"sub": user_email}, expires_delta=access_token_expires
        )
        
        # Track login activity
        if tracker:
            await tracker.track_user_login(
                user_email=user_email,
                user_name=user_name,
                user_picture=user_picture,
                login_method="google",
                ip_address=http_req.client.host,
                user_agent=http_req.headers.get("User-Agent")
            )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 3600
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login failed with exception: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

# Mock endpoints for testing (remove in production)
@router.post("/mock-login", response_model=Token)
async def mock_login(request: GoogleLoginRequest, http_req: Request):
    """Mock login for testing (remove in production)"""
    try:
        # Mock user information
        mock_user_email = "test@example.com"
        mock_user_name = "Test User"
        mock_user_picture = "https://example.com/avatar.jpg"
        
        # Create access token
        access_token_expires = None
        access_token = create_access_token(
            data={"sub": mock_user_email}, expires_delta=access_token_expires
        )
        
        # Track login activity
        if tracker:
            await tracker.track_user_login(
                user_email=mock_user_email,
                user_name=mock_user_name,
                user_picture=mock_user_picture,
                login_method="google",
                ip_address=http_req.client.host,
                user_agent=http_req.headers.get("User-Agent")
            )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 3600
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mock login failed: {str(e)}") 