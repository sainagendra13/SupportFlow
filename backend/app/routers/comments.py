
from fastapi import APIRouter, Depends
from bson import ObjectId
from app.config import settings
from app.csrf import require_csrf
from app.database import db
from app.authorisation import get_current_user
from app.schemas.ticket import CommentCreate, CommentResponse
from app.services.ticketservice import get_accessible_ticket,serialize,utcnow
from app.tasks.notification import ticket_commented


router = APIRouter(prefix="/api/tickets",tags=["Comments"],dependencies=[Depends(require_csrf)])


@router.post("/{ticket_id}/comments",response_model=CommentResponse,status_code=201)
async def add_comment(ticket_id: str,data: CommentCreate,user=Depends(get_current_user)):
    ticket = await get_accessible_ticket(ticket_id, user)
    comment = {
        "ticket_id": ticket_id,
        "author_id": str(user["_id"]),
        "message": data.message,
        "created_at": utcnow(),
    }

    result = await db.comments.insert_one(comment)
    comment["_id"] = result.inserted_id

    if settings.enable_jobs:
        try:
            ticket_commented.delay(
                ticket_id,
                ticket["owner_id"],
                user["role"],
                str(result.inserted_id),
            )
        except Exception:
            pass

    return {
    **serialize(comment),
    "author_name": user["name"],
    "author_role": user["role"],
}


@router.get("/{ticket_id}/comments",response_model=list[CommentResponse])
async def list_comments(ticket_id: str,user=Depends(get_current_user)):
    await get_accessible_ticket(ticket_id, user)

    cursor = (
        db.comments.find({"ticket_id": ticket_id})
        .sort("created_at", 1)
        .limit(200)
    )
    comments = [serialize(comment) async for comment in cursor]

    author_ids = {
        ObjectId(comment["author_id"])
        for comment in comments
        if ObjectId.is_valid(comment["author_id"])
    }

    users = db.users.find(
        {"_id": {"$in": list(author_ids)}},
        {"name": 1, "role": 1},
    )

    authors = {
        str(user["_id"]): user
        async for user in users
    }

    for comment in comments:
        author = authors.get(comment["author_id"], {})

        comment["author_name"] = author.get("name", "Unknown User")
        comment["author_role"] = author.get("role", "unknown")

    return comments
