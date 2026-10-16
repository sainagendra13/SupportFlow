from fastapi import APIRouter, Depends, HTTPException, Response
from pymongo.errors import DuplicateKeyError
from app.config import settings
from app.csrf import create_csrf_token, require_csrf
from app.database import db
from app.authorisation import get_current_user
from app.schemas.user import UserRegister, UserLogin, UserResponse
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def set_auth_cookies(response: Response, user_id: str):
    token = create_access_token(user_id)
    payload = decode_access_token(token)
    csrf_token = create_csrf_token(payload["jti"])
    max_age = settings.access_token_minutes * 60

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=max_age,
        path="/api",
    )

    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=max_age,
        path="/",
    )


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserRegister):
    user = {
        "name": data.name,
        "email": str(data.email).lower(),
        "password_hash": hash_password(data.password),
        "role": "customer",
    }

    try:
        result = await db.users.insert_one(user)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Email already registered")

    return {
        "id": str(result.inserted_id),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
    }


@router.post("/login")
async def login(data: UserLogin, response: Response):
    user = await db.users.find_one({"email": str(data.email).lower() })

    if not user or not verify_password(data.password,user["password_hash"]):
        raise HTTPException(status_code=401,detail="Invalid credentials")

    set_auth_cookies(response, str(user["_id"]))
    return {
        "message": "Login successful",
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
        },
    }


@router.get("/me", response_model=UserResponse)
async def me(user=Depends(get_current_user)):
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
    }


@router.post("/logout", dependencies=[Depends(require_csrf)])
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/api",
        secure=settings.cookie_secure,
        httponly=True,
        samesite="lax",
    )

    response.delete_cookie(
        key="csrf_token",
        path="/",
        secure=settings.cookie_secure,
        samesite="lax",
    )

    return {"message": "Logged out successfully"}
