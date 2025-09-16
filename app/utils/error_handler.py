from fastapi import HTTPException
import logging
import traceback

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base API error class"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def handle_service_error(e: Exception, operation: str) -> HTTPException:
    """Standardized error handling for service operations"""
    error_msg = f"{operation} failed: {str(e)}"
    logger.error(f"{error_msg}\n{traceback.format_exc()}")
    
    if isinstance(e, ValueError):
        return HTTPException(status_code=400, detail=error_msg)
    elif isinstance(e, APIError):
        return HTTPException(status_code=e.status_code, detail=e.message)
    else:
        return HTTPException(status_code=500, detail="Internal server error")

def safe_execute(operation: str):
    """Decorator for safe service execution"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                raise handle_service_error(e, operation)
        return wrapper
    return decorator