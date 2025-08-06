"""
Pydantic models for LexiDash API
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

# Authentication Models
class GoogleLoginRequest(BaseModel):
    id_token: str = Field(..., description="Google ID token")

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600

class User(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None

# Text Comparison Models
class TextComparisonRequest(BaseModel):
    original_text: str = Field(..., min_length=1, description="Original text to compare against")
    summary_text: str = Field(..., min_length=1, description="User's summary text")
    reading_mode: str = Field(default="detailed", description="Reading mode for analysis")
    wpm: Optional[int] = Field(default=None, ge=1, le=1000, description="Words per minute reading speed")
    lpm: Optional[int] = Field(default=None, ge=1, le=100, description="Lines per minute reading speed")
    source: Optional[str] = Field(default="web", description="Source of the request")
    session_id: Optional[str] = Field(default=None, description="Unique session identifier")
    user_agent: Optional[str] = Field(default=None, description="Browser user agent string")
    ip_address: Optional[str] = Field(default=None, description="Client IP address")
    category: Optional[str] = Field(default="educational", description="Content category")
    language: Optional[str] = Field(default="en", description="Content language")
    difficulty_level: Optional[str] = Field(default="medium", description="Content difficulty level")
    tags: Optional[List[str]] = Field(default=[], description="Array of tags for categorization")

class TextComparisonResponse(BaseModel):
    accuracy_score: int = Field(..., ge=0, le=100, description="Accuracy score from 0 to 100")
    correct_points: List[str] = Field(default=[], description="Correctly captured points")
    missed_points: List[str] = Field(default=[], description="Important points that were missed")
    wrong_points: List[str] = Field(default=[], description="Incorrect or misleading information")
    tracking_status: str = Field(default="tracked", description="Status of activity tracking")

# Code Summary Evaluation Models
class CodeSummaryEvaluationRequest(BaseModel):
    original_code: str = Field(..., min_length=1, description="Original code to evaluate against")
    summary_text: str = Field(..., min_length=1, description="User's summary of the code")
    language: str = Field(default="python", description="Programming language of the code")
    evaluation_mode: str = Field(default="comprehensive", description="Evaluation mode for analysis")
    source: Optional[str] = Field(default="web", description="Source of the request")
    session_id: Optional[str] = Field(default=None, description="Unique session identifier")
    user_agent: Optional[str] = Field(default=None, description="Browser user agent string")
    ip_address: Optional[str] = Field(default=None, description="Client IP address")
    category: Optional[str] = Field(default="educational", description="Content category")
    difficulty_level: Optional[str] = Field(default="medium", description="Code difficulty level")
    tags: Optional[List[str]] = Field(default=[], description="Array of tags for categorization")

class CodeSummaryEvaluationResponse(BaseModel):
    accuracy_score: int = Field(..., ge=0, le=100, description="Accuracy score from 0 to 100")
    correct_points: List[str] = Field(default=[], description="Correctly captured points about the code")
    missed_points: List[str] = Field(default=[], description="Important code aspects that were missed")
    wrong_points: List[str] = Field(default=[], description="Incorrect or misleading information about the code")
    tracking_status: str = Field(default="tracked", description="Status of activity tracking")

# Activity Models
class Activity(BaseModel):
    id: int
    user_email: str
    user_type: str
    activity_type: str
    accuracy_score: Optional[int] = None
    reading_mode: Optional[str] = None
    wpm: Optional[int] = None
    lpm: Optional[int] = None
    created_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class UserActivitiesResponse(BaseModel):
    user_email: str
    total_activities: int
    activities: List[Activity]

class GuestActivitiesResponse(BaseModel):
    total_guest_activities: int
    activities: List[Activity]

class ActivityStatsResponse(BaseModel):
    total_activities: int
    authenticated_users: int
    guest_activities: int
    average_accuracy: float
    most_popular_reading_mode: str
    activity_breakdown: Dict[str, int]

class PointsAnalysisResponse(BaseModel):
    total_activities: int
    points_analysis: Dict[str, Dict[str, Any]]

class ReadingModeAnalyticsResponse(BaseModel):
    total_activities: int
    reading_modes: Dict[str, Dict[str, Any]]
    most_popular_mode: str
    highest_accuracy_mode: str

class UserReadingModesResponse(BaseModel):
    user_email: str
    preferred_mode: str
    best_performing_mode: str
    mode_preferences: Dict[str, Dict[str, Any]]



# Error Models
class ErrorResponse(BaseModel):
    detail: str

# Health Check Models
class HealthCheckResponse(BaseModel):
    message: str
    version: str
    status: str 