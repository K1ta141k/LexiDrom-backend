"""
Code Dataset API
Provides endpoints for getting random code samples from the CodeSearchNet dataset
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

# Import the Code dataset service
from app.services.code_dataset_service import CodeDatasetService

# Create router
router = APIRouter()

# Global service instance
code_service = None

# Pydantic models for request/response
class CodeSampleResponse(BaseModel):
    code: str
    language: str
    difficulty: str
    source: str
    id: str
    length: int
    docstring: str = ""
    url: str = ""

class CodeSamplesResponse(BaseModel):
    samples: List[CodeSampleResponse]
    total_count: int

class CodeDatasetInfoResponse(BaseModel):
    is_loaded: bool
    total_samples: int
    dataset_name: str
    description: str
    available_languages: List[str]
    available_difficulties: List[str]
    language_distribution: dict
    difficulty_distribution: dict

@router.get("/random", response_model=CodeSampleResponse)
async def get_random_code(
    language: Optional[str] = Query(None, description="Programming language filter (python, javascript, java, go, php, ruby)"),
    difficulty: Optional[str] = Query(None, description="Difficulty level filter (beginner, intermediate, advanced)"),
    min_length: int = Query(50, description="Minimum code length in characters"),
    max_length: int = Query(2000, description="Maximum code length in characters")
):
    """
    Get a random code sample from the CodeSearchNet dataset
    
    Args:
        language: Programming language filter (optional)
        difficulty: Difficulty level filter (optional)
        min_length: Minimum code length in characters (default: 50)
        max_length: Maximum code length in characters (default: 2000)
    
    Returns:
        Random code sample with metadata
    """
    global code_service
    
    if not code_service or not code_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Code dataset service is not available. Please try again later."
        )
    
    # Validate parameters
    if min_length < 10:
        min_length = 10
    if max_length > 10000:
        max_length = 10000
    if min_length > max_length:
        min_length, max_length = max_length, min_length
    
    # Validate language if provided
    if language and language.lower() not in code_service.languages:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid language. Available languages: {', '.join(code_service.languages)}"
        )
    
    # Validate difficulty if provided
    if difficulty and difficulty.lower() not in code_service.difficulty_levels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid difficulty. Available difficulties: {', '.join(code_service.difficulty_levels)}"
        )
    
    # Get random code sample
    result = code_service.get_random_code(
        language=language,
        difficulty=difficulty,
        min_length=min_length,
        max_length=max_length
    )
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="No suitable code sample found with the specified criteria"
        )
    
    return CodeSampleResponse(**result)

@router.get("/random-multiple", response_model=CodeSamplesResponse)
async def get_random_codes(
    count: int = Query(1, ge=1, le=10, description="Number of code samples to return"),
    language: Optional[str] = Query(None, description="Programming language filter (python, javascript, java, go, php, ruby)"),
    difficulty: Optional[str] = Query(None, description="Difficulty level filter (beginner, intermediate, advanced)"),
    min_length: int = Query(50, description="Minimum code length in characters"),
    max_length: int = Query(2000, description="Maximum code length in characters")
):
    """
    Get multiple random code samples from the CodeSearchNet dataset
    
    Args:
        count: Number of code samples to return (1-10, default: 1)
        language: Programming language filter (optional)
        difficulty: Difficulty level filter (optional)
        min_length: Minimum code length in characters (default: 50)
        max_length: Maximum code length in characters (default: 2000)
    
    Returns:
        List of random code samples with metadata
    """
    global code_service
    
    if not code_service or not code_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Code dataset service is not available. Please try again later."
        )
    
    # Validate parameters
    if min_length < 10:
        min_length = 10
    if max_length > 10000:
        max_length = 10000
    if min_length > max_length:
        min_length, max_length = max_length, min_length
    
    # Validate language if provided
    if language and language.lower() not in code_service.languages:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid language. Available languages: {', '.join(code_service.languages)}"
        )
    
    # Validate difficulty if provided
    if difficulty and difficulty.lower() not in code_service.difficulty_levels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid difficulty. Available difficulties: {', '.join(code_service.difficulty_levels)}"
        )
    
    # Get random code samples
    results = code_service.get_random_codes(
        count=count,
        language=language,
        difficulty=difficulty,
        min_length=min_length,
        max_length=max_length
    )
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail="No suitable code samples found with the specified criteria"
        )
    
    # Convert to response model
    sample_responses = [CodeSampleResponse(**result) for result in results]
    
    return CodeSamplesResponse(
        samples=sample_responses,
        total_count=len(sample_responses)
    )

@router.get("/info", response_model=CodeDatasetInfoResponse)
async def get_dataset_info():
    """
    Get information about the CodeSearchNet dataset
    
    Returns:
        Dataset information including load status, statistics, and available filters
    """
    global code_service
    
    if not code_service:
        return CodeDatasetInfoResponse(
            is_loaded=False,
            total_samples=0,
            dataset_name="CodeSearchNet",
            description="A large-scale dataset of code functions from multiple programming languages",
            available_languages=[],
            available_difficulties=[],
            language_distribution={},
            difficulty_distribution={}
        )
    
    info = code_service.get_dataset_info()
    return CodeDatasetInfoResponse(**info)

@router.get("/languages")
async def get_available_languages():
    """
    Get list of available programming languages
    
    Returns:
        List of available programming languages
    """
    global code_service
    
    if not code_service or not code_service.is_available():
        return {"languages": []}
    
    languages = code_service.get_available_languages()
    return {"languages": languages}

@router.get("/difficulties")
async def get_available_difficulties():
    """
    Get list of available difficulty levels
    
    Returns:
        List of available difficulty levels
    """
    global code_service
    
    if not code_service or not code_service.is_available():
        return {"difficulties": []}
    
    difficulties = code_service.get_available_difficulties()
    return {"difficulties": difficulties}

@router.get("/health")
async def health_check():
    """
    Health check for the code dataset service
    
    Returns:
        Service health status
    """
    global code_service
    
    return {
        "service": "code-dataset",
        "status": "healthy" if code_service and code_service.is_available() else "unavailable",
        "dataset_loaded": code_service.is_available() if code_service else False,
        "total_samples": code_service.get_dataset_info()["total_samples"] if code_service else 0,
        "available_languages": code_service.get_available_languages() if code_service else [],
        "available_difficulties": code_service.get_available_difficulties() if code_service else []
    } 