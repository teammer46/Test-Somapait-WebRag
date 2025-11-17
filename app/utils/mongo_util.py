from pymongo import MongoClient, ASCENDING
from datetime import datetime
import os

from app.model.schemas import Chat


# ---------------------------------
# Mongo Connection
# ---------------------------------

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)

db = client["chatbot_db"]
collection = db["chat_history"]

# ---------------------------------
# Save Chat (เหมือนฟังก์ชันต้นฉบับของคุณ)
# ---------------------------------
def save_history_mongo(title: str, chat: Chat):
    now = datetime.now()

    chat_dict = chat.model_dump()

    existing = collection.find_one({"title": title})

    if existing is None:
        # สร้างห้องใหม่
        new_doc = {
            "title": title,
            "history": [chat_dict],
            "createAt": now,
            "updateAt": now
        }
        collection.insert_one(new_doc)
        return "created"

    else:
        # Append message ในห้องเดิม
        collection.update_one(
            {"title": title},
            {
                "$push": {"history": chat_dict},
                "$set": {"updateAt": now}
            }
        )
        return "updated"


# ---------------------------------
# List Histories
# ---------------------------------
def list_histories():
    sessions = collection.find({}, {"title": 1, "createAt": 1, "updateAt": 1}).sort("updateAt", -1)

    return [
        {
            "id": str(s["_id"]),
            "title": s.get("title"),
            "createAt": s.get("createAt"),
            "updateAt": s.get("updateAt")
        }
        for s in sessions
    ]

# ---------------------------------
# Load Chat History ตาม title
# ---------------------------------
def load_history_by_title(title: str):
    doc = collection.find_one({"title": title})
    if not doc:
        return []
    return doc["history"]


# ---------------------------------
# Delete Chat History ตาม ID
# ---------------------------------

def del_history(title):
    return collection.delete_one({"title": title})

# ---------------------------------
# Optional: Rename Chat Session
# ---------------------------------
def rename_title(old_title: str, new_title: str):
    result = collection.update_one(
        {"title": old_title},
        {"$set": {"title": new_title}}
    )
    return result.modified_count == 1
