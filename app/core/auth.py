"""
Authentication core module for LexiDash
Handles JWT tokens and Google OAuth verification
"""

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.auth.transport import requests
from google.oauth2 import id_token
from app.models.schemas import User

# Security scheme
security = HTTPBearer()

# JWT settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Google OAuth settings
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return payload
    except jwt.PyJWTError:
        return None

async def verify_google_token(token_str: str) -> Optional[dict]:
    """Verify Google token (ID token or access token) and return user info"""
    try:
        if not GOOGLE_CLIENT_ID:
            print("❌ GOOGLE_CLIENT_ID not configured")
            return None
        
        # First, try to verify as ID token
        try:
            idinfo = id_token.verify_oauth2_token(
                token_str, 
                requests.Request(), 
                GOOGLE_CLIENT_ID
            )
            
            # Check if the token is expired
            if idinfo['exp'] < datetime.utcnow().timestamp():
                print("❌ Google ID token expired")
                return None
            
            # Check if the token was issued for our app
            if idinfo['aud'] != GOOGLE_CLIENT_ID:
                print(f"❌ Token audience mismatch: expected {GOOGLE_CLIENT_ID}, got {idinfo['aud']}")
                return None
            
            return {
                "email": idinfo["email"],
                "name": idinfo.get("name"),
                "picture": idinfo.get("picture")
            }
        except Exception as id_token_error:
            print(f"⚠️ ID token verification failed: {id_token_error}")
            
            # If ID token fails, try to use the token as an access token to get user info
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "https://www.googleapis.com/oauth2/v2/userinfo",
                        headers={"Authorization": f"Bearer {token_str}"}
                    )
                    
                    if response.status_code == 200:
                        user_info = response.json()
                        return {
                            "email": user_info["email"],
                            "name": user_info.get("name"),
                            "picture": user_info.get("picture")
                        }
                    else:
                        print(f"❌ Failed to get user info from access token: {response.status_code}")
                        return None
                        
            except Exception as access_token_error:
                print(f"❌ Access token verification failed: {access_token_error}")
                return None
                
    except Exception as e:
        print(f"❌ Google token verification failed: {e}")
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return User(email=email)

def get_google_oauth_url() -> str:
    """Generate Google OAuth URL"""
    client_id = GOOGLE_CLIENT_ID
    redirect_uri = os.getenv("FRONTEND_URL", "http://localhost:3000") + "/auth/callback"
    scope = "openid email profile"
    
    auth_url = (
        f"https://accounts.google.com/oauth/authorize?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"response_type=id_token"
    )
    
    return auth_url 