
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException
from pymongo import ReturnDocument

from app.cache import clear_cache, get_cache, set_cache
from app.config import settings
from app.database import db
from app.tasks.notification import ticket_created


def utcnow():
    return datetime.now(timezone.utc)


def serialize(document):
    result = dict(document)
    result["id"] = str(result.pop("_id"))
    return result


def parse_id(value: str):
    if not ObjectId.is_valid(value):
        raise HTTPException(
            status_code=404,
            detail="Resource not found",
        )

    return ObjectId(value)


async def get_accessible_ticket(ticket_id: str, user: dict):
    query = {"_id": parse_id(ticket_id)}

    if user["role"] == "customer":
        query["owner_id"] = str(user["_id"])

    ticket = await db.tickets.find_one(query)

    if not ticket:
        raise HTTPException(404, "Ticket not found")

    return ticket


async def create_ticket(data, user: dict):
    if user["role"] != "customer":
        raise HTTPException(403, "Only customers can create tickets")

    owner_id = str(user["_id"])
    timestamp = utcnow()

    ticket = {
        **data.model_dump(),
        "status": "open",
        "owner_id": owner_id,
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    result = await db.tickets.insert_one(ticket)
    ticket["_id"] = result.inserted_id

    await clear_cache(
        f"stats:user:{owner_id}",
        "stats:all",
    )

    if settings.enable_jobs:
        try:
            ticket_created.delay(
                str(result.inserted_id),
                owner_id,
            )
        except Exception:
            pass

    return serialize(ticket)


async def list_tickets(
    user: dict,
    status: str | None,
    priority: str | None,
    skip: int,
    limit: int,
):
    query = {}

    if user["role"] == "customer":
        query["owner_id"] = str(user["_id"])

    if status:
        query["status"] = status

    if priority:
        query["priority"] = priority

    cursor = (
        db.tickets.find(query)
        .sort([("created_at", -1), ("_id", -1)])
        .skip(skip)
        .limit(limit)
    )

    return [serialize(ticket) async for ticket in cursor]


async def update_ticket(ticket_id: str, data):
    changes = data.model_dump(exclude_none=True)

    if not changes:
        raise HTTPException(
            status_code=422,
            detail="Provide status or priority",
        )

    changes["updated_at"] = utcnow()

    ticket = await db.tickets.find_one_and_update(
        {"_id": parse_id(ticket_id)},
        {"$set": changes},
        return_document=ReturnDocument.AFTER,
    )

    if not ticket:
        raise HTTPException(404, "Ticket not found")

    await clear_cache(
        f"stats:user:{ticket['owner_id']}",
        "stats:all",
    )

    return serialize(ticket)


async def get_dashboard_stats(user: dict):
    owner_id = str(user["_id"])

    cache_key = (
        f"stats:user:{owner_id}"
        if user["role"] == "customer"
        else "stats:all"
    )

    cached = await get_cache(cache_key)

    if cached is not None:
        return cached

    query = (
        {"owner_id": owner_id}
        if user["role"] == "customer"
        else {}
    )

    result = {
        "total": await db.tickets.count_documents(query)
    }

    for status in ("open", "in_progress", "resolved"):
        result[status] = await db.tickets.count_documents({
            **query,
            "status": status,
        })

    await set_cache(cache_key, result, ttl=30)

    return result
