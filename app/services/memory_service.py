import json
from typing import List, Dict

import redis


class RedisMemoryService:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0) -> None:
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def add_message(self, session_id: str, role: str, content: str) -> None:
        key = f"chat:{session_id}"
        message = {"role": role, "content": content}
        self.client.rpush(key, json.dumps(message))

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        key = f"chat:{session_id}"
        messages = self.client.lrange(key, 0, -1)
        return [json.loads(message) for message in messages]

    def clear_history(self, session_id: str) -> None:
        key = f"chat:{session_id}"
        self.client.delete(key)