"""
Text Comparison API routes
Handles text comparison using Google AI
"""

import asyncio
from fastapi import APIRouter, HTTPException, Request, Depends, Body
from app.models.schemas import TextComparisonRequest, TextComparisonResponse, User
from app.core.auth import get_current_user
from app.services.text_comparison_service import TextComparisonService
from app.services.activity_tracker import ActivityTracker
from typing import Optional

router = APIRouter()

# Global services (will be set by main.py)
tracker: Optional[ActivityTracker] = None
comparison_service: Optional[TextComparisonService] = None

@router.post("/", response_model=TextComparisonResponse)
async def compare_texts(
    request: TextComparisonRequest,
    http_req: Request = None
):
    """Compare original text with summary text (with optional authentication)"""
    global comparison_service
    try:
        # Try to get user from Authorization header if present
        user = None
        if http_req:
            auth_header = http_req.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                try:
                    token = auth_header.split(" ")[1]
                    from app.core.auth import verify_token
                    payload = verify_token(token)
                    if payload:
                        user = User(email=payload.get("sub"))
                        print(f"✅ Authenticated user: {user.email}")
                except Exception as e:
                    print(f"⚠️ Token verification failed: {e}")
                    user = None
            else:
                print("ℹ️ No authentication token provided, proceeding as guest")
        
        # Initialize comparison service if not available
        if not comparison_service:
            comparison_service = TextComparisonService()
        
        # Perform text comparison
        accuracy_score, correct_points, missed_points, wrong_points = await comparison_service.compare_texts(
            original_text=request.original_text,
            summary_text=request.summary_text,
            reading_mode=request.reading_mode
        )
        
        # Track activity
        tracking_status = "not_tracked"
        print(f"🔍 Checking tracker availability...")
        print(f"   Global tracker: {'✅ Available' if tracker else '❌ Not available'}")
        if tracker:
            print(f"   Tracker.supabase: {'✅ Available' if tracker.supabase else '❌ Not available'}")
            if tracker.supabase:
                connected = tracker.supabase.is_connected()
                print(f"   Supabase connection: {'✅ Connected' if connected else '❌ Not connected'}")
        
        if tracker:
            try:
                print(f"🔍 Starting activity tracking...")
                success = await tracker.track_text_comparison(
                    user_email=user.email if user else None,
                    original_text=request.original_text,
                    summary_text=request.summary_text,
                    accuracy_score=accuracy_score,
                    correct_points=correct_points,
                    missed_points=missed_points,
                    wrong_points=wrong_points,
                    reading_mode=request.reading_mode,
                    additional_params=request.dict(exclude={"original_text", "summary_text"}),
                    ip_address=http_req.client.host if http_req else None,
                    user_agent=http_req.headers.get("User-Agent") if http_req else None,
                )
                tracking_status = "tracked" if success else "failed"
                print(f"📊 Activity tracking result: {tracking_status}")
            except Exception as e:
                print(f"❌ Failed to track activity: {e}")
                tracking_status = "failed"
        else:
            print("⚠️ No tracker available for activity tracking")
        
        return TextComparisonResponse(
            accuracy_score=accuracy_score,
            correct_points=correct_points,
            missed_points=missed_points,
            wrong_points=wrong_points,
            tracking_status=tracking_status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text comparison failed: {str(e)}")

@router.post("/guest", response_model=TextComparisonResponse)
async def compare_texts_guest(
    req: TextComparisonRequest,
    http_req: Request
):
    """Compare texts for guest users (no authentication required)"""
    global comparison_service
    try:
        # Initialize comparison service if not available
        if not comparison_service:
            comparison_service = TextComparisonService()
        
        # Perform text comparison
        accuracy_score, correct_points, missed_points, wrong_points = await comparison_service.compare_texts(
            original_text=req.original_text,
            summary_text=req.summary_text,
            reading_mode=req.reading_mode
        )
        
        # Track activity
        tracking_status = "not_tracked"
        print(f"🔍 Checking guest tracker availability...")
        print(f"   Global tracker: {'✅ Available' if tracker else '❌ Not available'}")
        if tracker:
            print(f"   Tracker.supabase: {'✅ Available' if tracker.supabase else '❌ Not available'}")
            if tracker.supabase:
                connected = tracker.supabase.is_connected()
                print(f"   Supabase connection: {'✅ Connected' if connected else '❌ Not connected'}")
        
        if tracker:
            try:
                print(f"🔍 Starting guest activity tracking...")
                success = await tracker.track_text_comparison(
                    user_email=None,  # Guest user
                    original_text=req.original_text,
                    summary_text=req.summary_text,
                    accuracy_score=accuracy_score,
                    correct_points=correct_points,
                    missed_points=missed_points,
                    wrong_points=wrong_points,
                    reading_mode=req.reading_mode,
                    additional_params=req.dict(exclude={"original_text", "summary_text"}),
                    ip_address=http_req.client.host,
                    user_agent=http_req.headers.get("User-Agent"),
                )
                tracking_status = "tracked" if success else "failed"
                print(f"📊 Guest activity tracking result: {tracking_status}")
            except Exception as e:
                print(f"❌ Failed to track guest activity: {e}")
                tracking_status = "failed"
        else:
            print("⚠️ No tracker available for guest activity tracking")
        
        return TextComparisonResponse(
            accuracy_score=accuracy_score,
            correct_points=correct_points,
            missed_points=missed_points,
            wrong_points=wrong_points,
            tracking_status=tracking_status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text comparison failed: {str(e)}")

@router.post("/public", response_model=TextComparisonResponse)
async def compare_texts_public(
    req: TextComparisonRequest,
    http_req: Request,
    user: Optional[User] = None
):
    """Compare texts with optional authentication (for frontend compatibility)"""
    global comparison_service
    try:
        # Try to get user from Authorization header if present
        auth_header = http_req.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                from app.core.auth import verify_token
                payload = verify_token(token)
                if payload:
                    user = User(email=payload.get("sub"))
            except Exception as e:
                print(f"⚠️ Token verification failed: {e}")
                user = None
        
        # Initialize comparison service if not available
        if not comparison_service:
            comparison_service = TextComparisonService()
        
        # Perform text comparison
        accuracy_score, correct_points, missed_points, wrong_points = await comparison_service.compare_texts(
            original_text=req.original_text,
            summary_text=req.summary_text,
            reading_mode=req.reading_mode
        )
        
        # Track activity
        tracking_status = "not_tracked"
        if tracker:
            try:
                print(f"🔍 Starting public activity tracking...")
                success = await tracker.track_text_comparison(
                    user_email=user.email if user else None,
                    original_text=req.original_text,
                    summary_text=req.summary_text,
                    accuracy_score=accuracy_score,
                    correct_points=correct_points,
                    missed_points=missed_points,
                    wrong_points=wrong_points,
                    reading_mode=req.reading_mode,
                    additional_params=req.dict(exclude={"original_text", "summary_text"}),
                    ip_address=http_req.client.host,
                    user_agent=http_req.headers.get("User-Agent"),
                )
                tracking_status = "tracked" if success else "failed"
                print(f"📊 Public activity tracking result: {tracking_status}")
            except Exception as e:
                print(f"❌ Failed to track public activity: {e}")
                tracking_status = "failed"
        else:
            print("⚠️ No tracker available for public activity tracking")
        
        return TextComparisonResponse(
            accuracy_score=accuracy_score,
            correct_points=correct_points,
            missed_points=missed_points,
            wrong_points=wrong_points,
            tracking_status=tracking_status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text comparison failed: {str(e)}") 