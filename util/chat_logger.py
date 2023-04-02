from dotenv import load_dotenv
import pymongo
import os
import datetime

load_dotenv(override=True)

client = pymongo.MongoClient(os.environ.get("MONGO_URI"), maxPoolSize=50)

class ChatLogger:
    def __init__(self) -> None:
        self.log = client["line-bot"]["chat-log"]
        self.context = client["line-bot"]["context"]
        # Indexing for faster queries
        try:
            self.log.create_index(
                [("user_id", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)]
            )
        except pymongo.errors.OperationFailure:
            pass

    def log_message(self, user_id, user_name, role, message):
        self.log.insert_one(
            {
                "type": "message",
                "user_id": user_id,
                "user_name": user_name,
                "role": role,
                "message": message,
                "timestamp": datetime.datetime.now(),
            }
        )

    def retrieve_messages(self, user_id, limit=50, include_system=False):
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
        
    def block_user(self, user_id, user_name):
        self.log.insert_one(
            {
                "type": "block",
                "user_id": user_id,
                "user_name": user_name,
                "chat_after_block_count": 0,
                "timestamp": datetime.datetime.now(),
            }
        )
    
    def unblock_user(self, user_id):
        self.log.delete_one({"type": "block", "user_id": user_id})
    
    def is_blocked(self, user_id):
        return self.log.find_one({"type": "block", "user_id": user_id}) is not None
    
    def user_specific_context(self, user_id, user_name, context = ""):
        """ Get user specific context from database, if not found, create one"""
        if self.context.find_one({"user_id": user_id}) is None:
            self.context.insert_one(
                {
                    "user_id": user_id,
                    "user_name": user_name,
                    "context": context,
                    "timestamp": datetime.datetime.now(),
                }
            )

        return self.context.find_one({"user_id": user_id})["context"]
    
    def overwrite_user_specific_context(self, user_id, context):
        """ Overwrite user specific context from database, if not found, create one"""

        self.context.update_one(
            {"user_id": user_id},
            {"$set": {"context": context, "timestamp": datetime.datetime.now()}},
            )