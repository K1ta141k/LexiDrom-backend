"""
Random Text API
Provides endpoints for getting random text from the RACE dataset
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

# Import the RACE dataset service
from app.services.race_dataset_service import RACEDatasetService

# Create router
router = APIRouter()

# Global service instance
race_service = None

# Pydantic models for request/response
class RandomTextResponse(BaseModel):
    text: str
    source: str
    id: str
    length: int

class RandomTextsResponse(BaseModel):
    texts: List[RandomTextResponse]
    total_count: int

class DatasetInfoResponse(BaseModel):
    is_loaded: bool
    total_articles: int
    dataset_name: str
    description: str

@router.get("/random", response_model=RandomTextResponse)
async def get_random_text(
    min_length: int = Query(100, description="Minimum text length in characters"),
    max_length: int = Query(2000, description="Maximum text length in characters")
):
    """
    Get a random text from the RACE dataset
    
    Args:
        min_length: Minimum text length in characters (default: 100)
        max_length: Maximum text length in characters (default: 2000)
    
    Returns:
        Random text with metadata
    """
    global race_service
    
    if not race_service or not race_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="RACE dataset service is not available. Please try again later."
        )
    
    # Validate parameters
    if min_length < 10:
        min_length = 10
    if max_length > 10000:
        max_length = 10000
    if min_length > max_length:
        min_length, max_length = max_length, min_length
    
    # Get random text
    result = race_service.get_random_text(min_length, max_length)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="No suitable text found with the specified length constraints"
        )
    
    return RandomTextResponse(**result)

@router.get("/random-multiple", response_model=RandomTextsResponse)
async def get_random_texts(
    count: int = Query(1, ge=1, le=10, description="Number of texts to return"),
    min_length: int = Query(100, description="Minimum text length in characters"),
    max_length: int = Query(2000, description="Maximum text length in characters")
):
    """
    Get multiple random texts from the RACE dataset
    
    Args:
        count: Number of texts to return (1-10, default: 1)
        min_length: Minimum text length in characters (default: 100)
        max_length: Maximum text length in characters (default: 2000)
    
    Returns:
        List of random texts with metadata
    """
    global race_service
    
    if not race_service or not race_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="RACE dataset service is not available. Please try again later."
        )
    
    # Validate parameters
    if min_length < 10:
        min_length = 10
    if max_length > 10000:
        max_length = 10000
    if min_length > max_length:
        min_length, max_length = max_length, min_length
    
    # Get random texts
    results = race_service.get_random_texts(count, min_length, max_length)
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail="No suitable texts found with the specified length constraints"
        )
    
    # Convert to response model
    text_responses = [RandomTextResponse(**result) for result in results]
    
    return RandomTextsResponse(
        texts=text_responses,
        total_count=len(text_responses)
    )

@router.get("/info", response_model=DatasetInfoResponse)
async def get_dataset_info():
    """
    Get information about the RACE dataset
    
    Returns:
        Dataset information including load status and statistics
    """
    global race_service
    
    if not race_service:
        return DatasetInfoResponse(
            is_loaded=False,
            total_articles=0,
            dataset_name="RACE (Reading Comprehension from Examinations)",
            description="A large-scale reading comprehension dataset with articles from English exams"
        )
    
    info = race_service.get_dataset_info()
    return DatasetInfoResponse(**info)

@router.get("/health")
async def health_check():
    """
    Health check for the random text service
    
    Returns:
        Service health status
    """
    global race_service
    
    return {
        "service": "random-text",
        "status": "healthy" if race_service and race_service.is_available() else "unavailable",
        "dataset_loaded": race_service.is_available() if race_service else False,
        "total_articles": race_service.get_dataset_info()["total_articles"] if race_service else 0
    } 