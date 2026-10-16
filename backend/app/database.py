
from pymongo import AsyncMongoClient
from app.config import settings


client = AsyncMongoClient(settings.mongo_url)
db = client[settings.database_name]


async def connect_database():
    await client.admin.command("ping")
    from app.utils.db_init import initialize_database
    await initialize_database()
    await db.users.create_index("email", unique=True)
    await db.tickets.create_index([("owner_id", 1), ("created_at", -1)])
    await db.tickets.create_index([("status", 1), ("created_at", -1)])
    await db.comments.create_index([("ticket_id", 1), ("created_at", 1)])
    await db.notifications.create_index([("owner_id", 1), ("created_at", -1)])

async def close_database():
    await client.close()
