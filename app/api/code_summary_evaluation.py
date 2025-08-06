"""
Code Summary Evaluation API
Placeholder for code summary evaluation functionality
"""

from fastapi import APIRouter

# Create router
router = APIRouter()

# Global service instance
tracker = None
evaluation_service = None

@router.get("/health")
async def health_check():
    """
    Health check for the code summary evaluation service
    
    Returns:
        Service health status
    """
    return {
        "service": "code-summary-evaluation",
        "status": "not_implemented",
        "message": "Code summary evaluation service is not yet implemented"
    } 