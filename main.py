#!/usr/bin/env python3
"""
LexiDrom Backend - FastAPI Text Comparison Service
Main application entry point
"""

import os
import asyncio
import datetime
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Import application modules
from app.api import auth, text_comparison, activities, random_text, code, code_summary_evaluation
from app.core.auth import get_current_user
from app.services.activity_tracker import ActivityTracker
from app.services.supabase_manager import SupabaseManager
from app.services.race_dataset_service import RACEDatasetService
from app.services.code_dataset_service import CodeDatasetService
from app.models.schemas import User

# Environment variables
from dotenv import load_dotenv
load_dotenv()

# Global services
tracker = None
supabase = None
race_service = None
code_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global tracker, supabase
    
    # Startup
    print("🚀 Starting LexiDrom Backend...")
    
    # Initialize Supabase connection
    supabase = SupabaseManager()
    connection_success = await supabase.connect()
    
    if connection_success:
        print("✅ Supabase connection established")
    else:
        print("❌ Supabase connection failed - will retry on first use")
        # Don't set supabase to None, let it retry on first use
    
    # Initialize ActivityTracker
    tracker = ActivityTracker(supabase)
    print("✅ ActivityTracker initialized")
    
    # Initialize RACE Dataset Service
    race_service = RACEDatasetService()
    load_success = await race_service.load_dataset()
    if load_success:
        print("✅ RACE dataset loaded successfully")
    else:
        print("⚠️ RACE dataset loading failed - will retry on first use")
    
    # Initialize Code Dataset Service
    code_service = CodeDatasetService()
    code_load_success = await code_service.load_dataset()
    if code_load_success:
        print("✅ Code dataset loaded successfully")
    else:
        print("⚠️ Code dataset loading failed - will retry on first use")
    
    # Set global services for API routes
    auth.tracker = tracker
    text_comparison.tracker = tracker
    text_comparison.comparison_service = None  # Will be initialized on first use
    activities.supabase = supabase
    random_text.race_service = race_service
    code.code_service = code_service
    code_summary_evaluation.tracker = tracker
    code_summary_evaluation.evaluation_service = None  # Will be initialized on first use
    
    print(f"🔧 Global services initialized:")
    print(f"   Tracker: {'✅ Available' if tracker else '❌ Not available'}")
    print(f"   Supabase: {'✅ Available' if supabase else '❌ Not available'}")
    print(f"   RACE Dataset: {'✅ Available' if race_service and race_service.is_available() else '❌ Not available'}")
    print(f"   Code Dataset: {'✅ Available' if code_service and code_service.is_available() else '❌ Not available'}")
    if tracker and tracker.supabase:
        print(f"   Tracker-Supabase connection: {'✅ Available' if tracker.supabase else '❌ Not available'}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down LexiDrom Backend...")
    if supabase:
        await supabase.disconnect()

# Create FastAPI app
app = FastAPI(
    title="LexiDrom Text Comparison API",
    description="Advanced text comparison service with Google OAuth and Supabase integration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:8000",
        "http://192.168.1.173:3000",
        "http://192.168.1.173:8000",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5173",
        # Production domains - Update these with your actual domains
        "https://lexidrom.com",
        "https://www.lexidrom.com",
        "https://api.lexidrom.com",
        "https://app.lexidrom.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """Health check and API information"""
    return {
        "message": "LexiDrom Text Comparison API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.datetime.utcnow().isoformat(),
            "services": {
        "supabase": "unknown",
        "activity_tracker": "unknown",
        "race_dataset": "unknown",
        "code_dataset": "unknown"
    }
    }
    
    # Check service availability
    if supabase:
        health_status["services"]["supabase"] = "available"
    if tracker:
        health_status["services"]["activity_tracker"] = "available"
    if 'race_service' in globals() and race_service and race_service.is_available():
        health_status["services"]["race_dataset"] = "available"
    if 'code_service' in globals() and code_service and code_service.is_available():
        health_status["services"]["code_dataset"] = "available"
    
    return health_status

# Function to get current tracker (for dependency injection)
def get_tracker():
    return tracker

# Function to get current supabase (for dependency injection)
def get_supabase():
    return supabase

# Include API routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(text_comparison.router, prefix="/compare-texts", tags=["Text Comparison"])
app.include_router(activities.router, prefix="/activities", tags=["Activities"])
app.include_router(random_text.router, prefix="/random-text", tags=["Random Text"])
app.include_router(code.router, prefix="/code", tags=["Code Examples"])
app.include_router(code_summary_evaluation.router, prefix="/code-evaluation", tags=["Code Summary Evaluation"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    ) 