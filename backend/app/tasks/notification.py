
from datetime import datetime, timezone

from pymongo import MongoClient

from app.config import settings
from app.tasks.celery_app import celery_app


def utcnow():
    return datetime.now(timezone.utc)


def create_notification(db, notification_id, owner_id, ticket_id, message):
    db.notifications.update_one(
        {"_id": notification_id},
        {
            "$setOnInsert": {
                "owner_id": owner_id,
                "ticket_id": ticket_id,
                "message": message,
                "read": False,
                "created_at": utcnow(),
            }
        },
        upsert=True,
    )


@celery_app.task(
    name="ticket_created",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def ticket_created(ticket_id: str, owner_id: str):
    client = MongoClient(settings.mongo_url)

    try:
        db = client[settings.database_name]

        create_notification(
            db,
            f"ticket:{ticket_id}",
            owner_id,
            ticket_id,
            "Your support ticket was created",
        )

        staff = db.users.find(
            {"role": {"$in": ["agent", "admin"]}},
            {"_id": 1},
        )

        for user in staff:
            staff_id = str(user["_id"])

            create_notification(
                db,
                f"ticket:{ticket_id}:staff:{staff_id}",
                staff_id,
                ticket_id,
                "A new customer ticket was created",
            )

        return {"processed": True, "ticket_id": ticket_id}

    finally:
        client.close()


@celery_app.task(
    name="ticket_updated",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def ticket_updated(
    ticket_id: str,
    owner_id: str,
    changes: dict,
    event_id: str,
):
    description = ", ".join(
        f"{field} to {str(value).replace('_', ' ')}"
        for field, value in changes.items()
    )

    client = MongoClient(settings.mongo_url)

    try:
        db = client[settings.database_name]

        create_notification(
            db,
            f"update:{event_id}:{owner_id}",
            owner_id,
            ticket_id,
            f"Your ticket was updated: {description}",
        )

        return {"processed": True, "ticket_id": ticket_id}

    finally:
        client.close()


@celery_app.task(
    name="ticket_commented",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def ticket_commented(
    ticket_id: str,
    owner_id: str,
    author_role: str,
    event_id: str,
):
    client = MongoClient(settings.mongo_url)

    try:
        db = client[settings.database_name]

        if author_role == "customer":
            staff = db.users.find(
                {"role": {"$in": ["agent", "admin"]}},
                {"_id": 1},
            )

            for user in staff:
                staff_id = str(user["_id"])

                create_notification(
                    db,
                    f"comment:{event_id}:{staff_id}",
                    staff_id,
                    ticket_id,
                    "A customer commented on a ticket",
                )

        else:
            create_notification(
                db,
                f"comment:{event_id}:{owner_id}",
                owner_id,
                ticket_id,
                "Support staff replied to your ticket",
            )

        return {"processed": True, "ticket_id": ticket_id}

    finally:
        client.close()
