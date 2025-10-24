from fastapi import Header, HTTPException, status
from .settings import settings

async def validate_token(authorization: str | None = Header(default=None)):
    if settings.API_TOKEN:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
        token = authorization.split(" ", 1)[1]
        if token != settings.API_TOKEN:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
