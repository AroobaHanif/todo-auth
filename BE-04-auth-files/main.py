from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from supabase_client import supabase
from auth import get_current_user, bearer_scheme

app = FastAPI(title="Auth API", version="1.0")


class Credentials(BaseModel):
    email: str
    password: str


@app.get("/public/info", tags=["Public"], summary="Public info, no auth required")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.post("/auth/signup", status_code=201, tags=["Auth"], summary="Create a new account")
def signup(payload: Credentials):
    if not payload.email or not payload.password:
        raise HTTPException(status_code=400, detail="email and password are required")

    try:
        result = supabase.auth.sign_up({"email": payload.email, "password": payload.password})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"user": result.user}


@app.post("/auth/login", tags=["Auth"], summary="Log in and receive a JWT")
def login(payload: Credentials):
    if not payload.email or not payload.password:
        raise HTTPException(status_code=400, detail="email and password are required")

    try:
        result = supabase.auth.sign_in_with_password(
            {"email": payload.email, "password": payload.password}
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

    return {
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token,
    }


@app.post("/auth/logout", status_code=204, tags=["Auth"], summary="Log out (protected)")
def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    return


@app.get("/protected/profile", tags=["Protected"], summary="Read your own profile")
def protected_profile(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
    }


@app.get("/protected/dashboard", tags=["Protected"], summary="Second protected route (proves the dependency is reusable)")
def protected_dashboard(user=Depends(get_current_user)):
    return {"message": f"Welcome back, {user.email}. This route is protected too."}
