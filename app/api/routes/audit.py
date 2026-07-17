from fastapi import APIRouter, Depends

from app.api.dependencies import require_role
from app.services.audit_logger import AuditLoggerService

router = APIRouter()

audit_logger = AuditLoggerService()


@router.get("/logs")
async def get_logs(date: str = None, level: str = None, category: str = None,
                   current_user: dict = Depends(require_role("admin"))):
    logs = await audit_logger.get_logs(date=date, level=level, category=category)
    return {"logs": logs, "count": len(logs)}


@router.get("/alerts")
async def get_alerts(level: str = None, current_user: dict = Depends(require_role("admin"))):
    alerts = await audit_logger.get_alerts(level=level)
    return {"alerts": alerts, "count": len(alerts)}