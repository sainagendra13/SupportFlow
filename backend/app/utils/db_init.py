
from app.database import db


async def initialize_database():
    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["role"],
            "properties": {
                "role": {
                    "bsonType": "string",
                    "enum": ["customer", "agent", "admin"],
                    "description": "Invalid user role",
                }
            },
        }
    }

    collections = await db.list_collection_names()

    if "users" not in collections:
        await db.create_collection(
            "users",
            validator=validator,
            validationLevel="strict",
            validationAction="error",
        )
    else:
        await db.command({
            "collMod": "users",
            "validator": validator,
            "validationLevel": "strict",
            "validationAction": "error",
        })
