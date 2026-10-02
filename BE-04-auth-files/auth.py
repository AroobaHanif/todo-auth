from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from supabase_client import supabase

bearer_scheme = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """Reusable dependency: verifies the bearer token with Supabase and
    returns the user, or raises 401. Apply this to any protected route
    with `user = Depends(get_current_user)`."""
    token = credentials.credentials if credentials else None
    if not token:
        raise HTTPException(status_code=401, detail="Access token required")

    try:
        result = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if result is None or result.user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return result.user
