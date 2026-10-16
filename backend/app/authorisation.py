from bson import ObjectId
from fastapi import Depends, HTTPException, Request
from app.database import db
from app.security import decode_access_token


def get_token_payload(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token" )
    return payload


async def get_current_user(payload=Depends(get_token_payload)):
    user_id = payload["sub"]

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=401,detail="Invalid user identifier")

    user = await db.users.find_one({"_id": ObjectId(user_id) })

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


async def require_agent(user=Depends(get_current_user)):
    if user["role"] not in ("agent", "admin"):
        raise HTTPException(status_code=403, detail="Agent access required")
    return user



async def require_customer(
    user=Depends(get_current_user),
):
    if user["role"] != "customer":
        raise HTTPException(
            status_code=403,
            detail="Only customers can create tickets",
        )
    return user

async def require_admin(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    return user