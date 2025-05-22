from functools import wraps
from fastapi import Request, HTTPException, status


def login_required(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logged in")
        return await func(request, *args, **kwargs)
    return wrapper
