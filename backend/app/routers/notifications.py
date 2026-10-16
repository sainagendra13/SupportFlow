
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query

from app.csrf import require_csrf
from app.database import db
from app.authorisation import get_current_user


router = APIRouter(prefix="/api/notifications",tags=["Notifications"],dependencies=[Depends(require_csrf)])


def serialize_notification(notification):
    return {
        "id": str(notification["_id"]),
        "ticket_id": notification["ticket_id"],
        "message": notification["message"],
        "read": notification.get("read", False),
        "created_at": notification["created_at"],
    }


@router.get("")
async def list_notifications(limit: int = Query(30, ge=1, le=100),user=Depends(get_current_user)):
    owner_id = str(user["_id"])
    cursor = (
        db.notifications.find({"owner_id": owner_id})
        .sort("created_at", -1)
        .limit(limit)
    )
    notifications = [ serialize_notification(item) async for item in cursor]

    unread_count = await db.notifications.count_documents({
        "owner_id": owner_id,
        "read": {"$ne": True},
    })

    return {
        "notifications": notifications,
        "unread_count": unread_count,
    }


@router.patch("/read-all")
async def mark_all_read(user=Depends(get_current_user)):
    result = await db.notifications.update_many(
        {"owner_id": str(user["_id"]), "read": {"$ne": True}},
        {"$set": {"read": True}}
    )

    return {"updated": result.modified_count}


@router.patch("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    user=Depends(get_current_user),
):
    possible_ids = [notification_id]

    if ObjectId.is_valid(notification_id):
        possible_ids.append(ObjectId(notification_id))

    result = await db.notifications.update_one(
        {
            "_id": {"$in": possible_ids},
            "owner_id": str(user["_id"]),
        },
        {"$set": {"read": True}})

    if not result.matched_count:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    return {"message": "Notification marked as read"}
