from dotenv import load_dotenv
import pymongo
import os
import datetime

load_dotenv(override=True)

client = pymongo.MongoClient(os.environ.get("MONGO_URI"), maxPoolSize=50)

class ChatLogger:
    def __init__(self) -> None:
        self.log = client["line-bot"]["chat-log"]
        # Indexing for faster queries
        try:
            self.log.create_index(
                [("user_id", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)]
            )
        except pymongo.errors.OperationFailure:
            pass

    def log_message(self, user_id, role, message):
        self.log.insert_one(
            {
                "type": "message",
                "user_id": user_id,
                "role": role,
                "message": message,
                "timestamp": datetime.datetime.now(),
            }
        )

    def retrieve_messages(self, user_id, limit=10, include_system=False):
        # List Comprehension to filter out system messages
        messages = [
            {"role": message["role"], "content": message["message"]}
            for message in self.log.find({"user_id": user_id})
            .sort("timestamp", pymongo.DESCENDING)
            .limit(limit)
            if include_system or message["role"] not in ["system", "assistant"]
        ]
        return messages

    def purge_messages(self, user_id):
        self.log.delete_many({"user_id": user_id})
