
from datetime import datetime
from typing import Literal

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from pymongo import ReturnDocument

from app.csrf import require_csrf
from app.database import db
from app.authorisation import require_admin


router = APIRouter(
    prefix="/api/admin",
    tags=["Administration"],
    dependencies=[Depends(require_admin), Depends(require_csrf)],
)


class RoleUpdate(BaseModel):
    role: Literal["customer", "agent"]


def serialize_user(user):
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
    }


@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    users = (
        db.users.find(
            {},
            {"password_hash": 0},
        )
        .sort("name", 1)
        .skip(skip)
        .limit(limit)
    )

    results = [serialize_user(user) async for user in users]
    total = await db.users.count_documents({})

    return {
        "total": total,
        "users": results,
    }


@router.patch("/users/{user_id}/role")
async def update_user_role(user_id: str,data: RoleUpdate):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=404,detail="User not found")

    user = await db.users.find_one_and_update(
        {
            "_id": ObjectId(user_id),
            "role": {"$in": ["customer", "agent"]},
        },
        {"$set": {"role": data.role}},
        return_document=ReturnDocument.AFTER,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found or role cannot be changed",
        )

    return serialize_user(user)
