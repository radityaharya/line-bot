from dotenv import load_dotenv
import pymongo
import os
import datetime
import bson
import logging

load_dotenv(override=True)

client = pymongo.MongoClient(os.environ.get("MONGO_URI"), maxPoolSize=50)

logger = logging.getLogger("line-bot")


class ChatLogger:
    def __init__(self) -> None:
        self.log = client["line-bot"]["chat-log"]
        self.user_config = client["line-bot"]["user-config"]
        self.config = client["line-bot"]["config"]
        # Indexing for faster queries
        try:
            self.log.create_index(
                [("user_id", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)]
            )
        except pymongo.errors.OperationFailure:
            pass

    def log_message(self, user_id, user_name, role, message, usage=None):
        self.log.insert_one(
            {
                "type": "message",
                "user_id": user_id,
                "user_name": user_name,
                "role": role,
                "message": message,
                "timestamp": datetime.datetime.now(),
                "usage": usage,
            }
        )

    def retrieve_messages(self, user_id, limit=None, include_system=False):
        if not limit:
            limit = self.config.find_one()["chat_context_limit"]
        messages = [
            {"role": message["role"], "content": message["message"]}
            for message in self.log.find({"user_id": user_id})
            .sort("timestamp", pymongo.DESCENDING)
            .limit(limit)
            if include_system or message["role"] not in ["system", "assistant"]
        ]
        return messages

    def purge_messages(self, user_id):
        logger.info(f"🗑️ Purging messages for {user_id}")
        self.log.delete_many({"user_id": user_id})

    def delete_n_number_of_messages(self, user_id, n):
        logger.info(f"🗑️ Deleting {n} messages for {user_id}")
        for message in (
            self.log.find({"user_id": user_id})
            .sort("timestamp", pymongo.ASCENDING)
            .limit(n)
        ):
            self.log.delete_one({"_id": message["_id"]})

    def block_user(self, user_id, user_name):
        self.user_config.find_one_and_update(
            {"user_id": user_id}, {"$set": {"is_blocked": True}}
        )
        logger.info(f"🔒 Blocked {user_id}")

    def unblock_user(self, user_id):
        self.user_config.find_one_and_update(
            {"user_id": user_id}, {"$set": {"is_blocked": False}}
        )
        logger.info(f"🔓 Unblocked {user_id}")

    def is_blocked(self, user_id):
        return self.user_config.find_one({"user_id": user_id})["is_blocked"]

    def user_specific_context(self, user_id, user_name, context=""):
        return self.user_config.find_one({"user_id": user_id})["user_context"]

    def overwrite_user_specific_context(self, user_id, context):
        self.user_config.find_one_and_update(
            {"user_id": user_id}, {"$set": {"user_context": context}}
        )
        logger.info(f"📝 Overwriting user context for {user_id}")
