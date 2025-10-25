from fastapi import Header, HTTPException, status
from .settings import settings

def _unauth():
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

async def validate_token(authorization: str | None = Header(default=None)) -> None:
    if not settings.API_TOKEN or not settings.API_TOKEN.strip():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: API token not set"
        )

    if not authorization:
        _unauth()

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        _unauth()

    if token.strip() != settings.API_TOKEN:
        _unauth()
