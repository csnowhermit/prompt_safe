import json
import time
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from app.config import settings
from app.core.redis_client import redis_client


class SessionManagerService:
    def __init__(self):
        self.session_prefix = "session:"
        self.max_turns = settings.session_max_turns
        self.max_duration = settings.session_max_duration_minutes
        self.idle_timeout = settings.session_idle_timeout_minutes
        self.max_tokens = settings.context_max_tokens

    async def create_session(self, user_id: str, role: str = "end_user") -> str:
        session_id = str(uuid4())
        now = datetime.utcnow().isoformat()

        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "status": "active",
            "created_at": now,
            "last_active_at": now,
            "expires_at": (datetime.utcnow() + timedelta(minutes=self.max_duration)).isoformat(),
            "turn_count": 0,
            "max_turns": self.max_turns,
            "context": [],
            "token_usage": {
                "current": 0,
                "max": self.max_tokens,
                "system_prompt_tokens": 0
            }
        }

        try:
            await redis_client.set(
                f"{self.session_prefix}{session_id}",
                json.dumps(session_data),
                ex=self.max_duration * 60
            )
        except Exception:
            pass

        return session_id

    async def get_session(self, session_id: str) -> dict:
        try:
            data = await redis_client.get(f"{self.session_prefix}{session_id}")
            if not data:
                return None
            return json.loads(data)
        except Exception:
            return None

    async def update_session(self, session_id: str, updates: dict) -> bool:
        data = await self.get_session(session_id)
        if not data:
            return False

        data.update(updates)
        data["last_active_at"] = datetime.utcnow().isoformat()

        try:
            await redis_client.set(
                f"{self.session_prefix}{session_id}",
                json.dumps(data),
                ex=self.max_duration * 60
            )
        except Exception:
            pass
        return True

    async def add_message(self, session_id: str, role: str, content: str,
                         risk_level: str = "green", sanitized: bool = True) -> bool:
        data = await self.get_session(session_id)
        if not data:
            return False

        if data["turn_count"] >= self.max_turns:
            return False

        message = {
            "role": role,
            "content": content,
            "hash": self._hash_content(content),
            "risk_level": risk_level,
            "sanitized": sanitized,
            "timestamp": datetime.utcnow().isoformat()
        }

        data["context"].append(message)
        data["turn_count"] += 1
        data["last_active_at"] = datetime.utcnow().isoformat()
        data["token_usage"]["current"] += len(content)

        data["context"] = self._sliding_window_truncate(data["context"])

        try:
            await redis_client.set(
                f"{self.session_prefix}{session_id}",
                json.dumps(data),
                ex=self.max_duration * 60
            )
        except Exception:
            pass
        return True

    def _sliding_window_truncate(self, context: list) -> list:
        system_msgs = [m for m in context if m.get("persistent")]
        history_msgs = [m for m in context if not m.get("persistent")]

        system_tokens = sum(len(m.get("content", "")) for m in system_msgs)
        budget = self.max_tokens - system_tokens

        kept = []
        token_sum = 0
        for msg in reversed(history_msgs):
            t = len(msg.get("content", ""))
            if token_sum + t > budget:
                break
            kept.insert(0, msg)
            token_sum += t

        return system_msgs + kept

    def _hash_content(self, content: str) -> str:
        import hashlib
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    async def terminate_session(self, session_id: str) -> bool:
        data = await self.get_session(session_id)
        if not data:
            return False

        data["status"] = "terminated"
        data["last_active_at"] = datetime.utcnow().isoformat()

        try:
            await redis_client.set(
                f"{self.session_prefix}{session_id}",
                json.dumps(data),
                ex=30 * 60
            )
        except Exception:
            pass
        return True

    async def is_session_active(self, session_id: str) -> bool:
        data = await self.get_session(session_id)
        if not data:
            return False

        if data["status"] != "active":
            return False

        expires_at = datetime.fromisoformat(data["expires_at"])
        if datetime.utcnow() > expires_at:
            data["status"] = "expired"
            try:
                await redis_client.set(f"{self.session_prefix}{session_id}", json.dumps(data), ex=30 * 60)
            except Exception:
                pass
            return False

        return True

    async def get_user_sessions(self, user_id: str) -> list:
        try:
            all_keys = await redis_client.keys(f"{self.session_prefix}*")
            sessions = []
            for key in all_keys:
                data = await redis_client.get(key)
                if data:
                    session_data = json.loads(data)
                    if session_data.get("user_id") == user_id:
                        sessions.append(session_data)
            return sessions
        except Exception:
            return []