from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import os
from supabase import create_client

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
app = FastAPI()


class Creds(BaseModel):
    email: str
    password: str


def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Access token required")
    token = authorization.replace("Bearer ", "")
    try:
        user = supabase.auth.get_user(token)
        return user.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.post("/auth/signup")
def signup(creds: Creds):
    result = supabase.auth.sign_up({"email": creds.email, "password": creds.password})
    return {"user": result.user}


@app.post("/auth/login")
def login(creds: Creds):
    result = supabase.auth.sign_in_with_password({"email": creds.email, "password": creds.password})
    return {"access_token": result.session.access_token}


@app.get("/protected/profile")
def profile(user=None, authorization: Optional[str] = Header(None)):
    user = verify_token(authorization)
    return {"id": user.id, "email": user.email}
