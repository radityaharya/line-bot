import logging


# custom log handler using mongodb
class MongoLogHandler(logging.StreamHandler):
    def __init__(self, collection):
        super().__init__()
        self.collection = collection

    def emit(self, record):
        if isinstance(record.msg, str):
            if record.msg.startswith("[MESSAGE]"):
                msg = record.msg.split(" ")
                user_name = msg[1]
                user_id = msg[2].replace("(", "").replace("):", "")
                message = " ".join(msg[3:])
                self.collection.insert_one(
                    {
                        "type": "message",
                        "user_name": user_name,
                        "user_id": user_id,
                        "message": message,
                        "timestamp": record.created,
                    }
                )
        self.collection.insert_one(
            {
                "type": "log",
                "name": record.name,
                "funcName": record.funcName,
                "level": record.levelname,
                "message": record.msg,
                "timestamp": record.created,
            }
        )
