import json
from datetime import datetime
from uuid import UUID

from app.config import settings
from app.core.security_context import LogLevel, EventCategory
from app.core.redis_client import redis_client


class AuditLoggerService:
    def __init__(self):
        self.log_prefix = "audit:log:"
        self.alert_prefix = "audit:alert:"

    async def log(self, timestamp: str = None, level: str = "INFO",
                  category: str = "SECURITY", trace_id: str = "",
                  span_id: str = "", event: str = "", details: dict = None,
                  user_hash: str = "", session_id: str = "",
                  latency_ms: float = 0.0) -> None:
        log_entry = {
            "timestamp": timestamp or datetime.utcnow().isoformat(),
            "level": level,
            "category": category,
            "trace_id": trace_id,
            "span_id": span_id,
            "event": event,
            "details": details or {},
            "user_hash": user_hash,
            "session_id": session_id,
            "latency_ms": latency_ms
        }

        log_key = f"{self.log_prefix}{datetime.utcnow().strftime('%Y%m%d')}"
        try:
            await redis_client.rpush(log_key, json.dumps(log_entry))

            if level in ["WARN", "ERROR", "CRITICAL"]:
                await self._trigger_alert(log_entry)
        except Exception:
            pass

    async def _trigger_alert(self, log_entry: dict) -> None:
        alert_key = f"{self.alert_prefix}{log_entry['level']}"
        try:
            await redis_client.rpush(alert_key, json.dumps(log_entry))
        except Exception:
            pass

    async def get_logs(self, date: str = None, level: str = None,
                       category: str = None) -> list:
        if date is None:
            date = datetime.utcnow().strftime('%Y%m%d')

        log_key = f"{self.log_prefix}{date}"
        try:
            logs = await redis_client.lrange(log_key, 0, -1)

            results = []
            for log in logs:
                entry = json.loads(log)
                if level and entry["level"] != level:
                    continue
                if category and entry["category"] != category:
                    continue
                results.append(entry)

            return results
        except Exception:
            return []

    async def get_alerts(self, level: str = None) -> list:
        try:
            if level:
                alert_key = f"{self.alert_prefix}{level}"
                alerts = await redis_client.lrange(alert_key, 0, -1)
            else:
                alerts = []
                for lvl in ["WARN", "ERROR", "CRITICAL"]:
                    alert_key = f"{self.alert_prefix}{lvl}"
                    alerts.extend(await redis_client.lrange(alert_key, 0, -1))

            return [json.loads(a) for a in alerts]
        except Exception:
            return []

    async def record_security_event(self, trace_id: str, event_type: str,
                                    risk_level: str, layer: str, rule_id: str = "",
                                    user_hash: str = "", session_id: str = "",
                                    details: dict = None) -> None:
        await self.log(
            level=self._get_log_level(risk_level),
            category="SECURITY",
            trace_id=trace_id,
            event=event_type,
            details=details or {
                "layer": layer,
                "rule_id": rule_id,
                "risk_level": risk_level
            },
            user_hash=user_hash,
            session_id=session_id
        )

    def _get_log_level(self, risk_level: str) -> str:
        mapping = {
            "green": "INFO",
            "yellow": "WARN",
            "red": "ERROR",
            "critical": "CRITICAL"
        }
        return mapping.get(risk_level, "INFO")