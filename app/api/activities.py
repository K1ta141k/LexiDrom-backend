"""
Activities API routes
Handles activity analytics and user activity tracking
"""

from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import (
    UserActivitiesResponse, GuestActivitiesResponse, ActivityStatsResponse,
    PointsAnalysisResponse, ReadingModeAnalyticsResponse, UserReadingModesResponse,
    Activity, User
)
from app.core.auth import get_current_user
from app.services.supabase_manager import SupabaseManager
from typing import Optional

router = APIRouter()

# Global supabase (will be set by main.py)
supabase: Optional[SupabaseManager] = None

@router.get("/user/{email}", response_model=UserActivitiesResponse)
async def get_user_activities(email: str, current_user: User = Depends(get_current_user)):
    """Get activities for a specific user"""
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Database not available")
        
        activities = await supabase.get_user_activities(email, limit=100)
        
        return UserActivitiesResponse(
            user_email=email,
            total_activities=len(activities),
            activities=activities
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user activities: {str(e)}")

@router.get("/guest", response_model=GuestActivitiesResponse)
async def get_guest_activities(current_user: User = Depends(get_current_user)):
    """Get all guest activities"""
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Database not available")
        
        activities = await supabase.get_guest_activities(limit=100)
        
        return GuestActivitiesResponse(
            total_guest_activities=len(activities),
            activities=activities
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get guest activities: {str(e)}")

@router.get("/stats", response_model=ActivityStatsResponse)
async def get_activity_stats(current_user: User = Depends(get_current_user)):
    """Get overall activity statistics"""
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Database not available")
        
        stats = await supabase.get_activity_stats()
        
        if not stats:
            # Return default stats
            return ActivityStatsResponse(
                total_activities=0,
                authenticated_users=0,
                guest_activities=0,
                average_accuracy=0.0,
                most_popular_reading_mode="detailed",
                activity_breakdown={}
            )
        
        return ActivityStatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get activity stats: {str(e)}")

@router.get("/points-analysis", response_model=PointsAnalysisResponse)
async def get_points_analysis(current_user: User = Depends(get_current_user)):
    """Get detailed analysis of points across all activities"""
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Database not available")
        
        analysis = await supabase.get_points_analysis()
        
        if not analysis:
            # Return default analysis
            return PointsAnalysisResponse(
                total_activities=0,
                points_analysis={
                    "correct_points": {"total_count": 0, "most_common": []},
                    "missed_points": {"total_count": 0, "most_common": []},
                    "wrong_points": {"total_count": 0, "most_common": []}
                }
            )
        
        return PointsAnalysisResponse(**analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get points analysis: {str(e)}")

@router.get("/reading-modes/analytics", response_model=ReadingModeAnalyticsResponse)
async def get_reading_modes_analytics(current_user: User = Depends(get_current_user)):
    """Get analytics for reading modes"""
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Database not available")
        
        analytics = await supabase.get_reading_modes_analytics()
        
        if not analytics:
            # Return default analytics
            return ReadingModeAnalyticsResponse(
                total_activities=0,
                reading_modes={},
                most_popular_mode="detailed",
                highest_accuracy_mode="detailed"
            )
        
        return ReadingModeAnalyticsResponse(**analytics)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get reading modes analytics: {str(e)}")

@router.get("/user/{email}/reading-modes", response_model=UserReadingModesResponse)
async def get_user_reading_modes(email: str, current_user: User = Depends(get_current_user)):
    """Get reading mode preferences for a specific user"""
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Database not available")
        
        modes = await supabase.get_user_reading_modes(email)
        
        if not modes:
            # Return default modes
            return UserReadingModesResponse(
                user_email=email,
                preferred_mode="detailed",
                best_performing_mode="detailed",
                mode_preferences={}
            )
        
        return UserReadingModesResponse(**modes)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user reading modes: {str(e)}")

@router.get("/user/{email}/points", response_model=PointsAnalysisResponse)
async def get_user_points_analysis(email: str, current_user: User = Depends(get_current_user)):
    """Get detailed points summary for a specific user"""
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Get user activities
        activities = await supabase.get_user_activities(email, limit=1000)
        
        # Analyze points
        correct_points = []
        missed_points = []
        wrong_points = []
        
        for activity in activities:
            if hasattr(activity, 'correct_points') and activity.correct_points:
                correct_points.extend(activity.correct_points)
            if hasattr(activity, 'missed_points') and activity.missed_points:
                missed_points.extend(activity.missed_points)
            if hasattr(activity, 'wrong_points') and activity.wrong_points:
                wrong_points.extend(activity.wrong_points)
        
        # Count occurrences
        def count_points(points_list):
            point_counts = {}
            for point in points_list:
                point_counts[point] = point_counts.get(point, 0) + 1
            return sorted(point_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return PointsAnalysisResponse(
            total_activities=len(activities),
            points_analysis={
                "correct_points": {
                    "total_count": len(correct_points),
                    "most_common": [{"point": p, "frequency": f} for p, f in count_points(correct_points)]
                },
                "missed_points": {
                    "total_count": len(missed_points),
                    "most_common": [{"point": p, "frequency": f} for p, f in count_points(missed_points)]
                },
                "wrong_points": {
                    "total_count": len(wrong_points),
                    "most_common": [{"point": p, "frequency": f} for p, f in count_points(wrong_points)]
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user points analysis: {str(e)}") 