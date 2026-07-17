from uuid import UUID

from fastapi import APIRouter

from app.schemas.input_guard import InputGuardRequest, InputGuardResponse
from app.services.input_guard import InputGuardService
from app.services.audit_logger import AuditLoggerService

router = APIRouter()

input_guard = InputGuardService()
audit_logger = AuditLoggerService()


@router.post("/check", response_model=InputGuardResponse)
async def check_input(request: InputGuardRequest):
    trace_id = UUID(request.trace_id) if request.trace_id else None
    session_id = UUID(request.session_id) if request.session_id else None

    result = await input_guard.process(
        request.text,
        request.user_id,
        request.role,
        trace_id=trace_id,
        session_id=session_id,
        mode=request.context.get("mode", "chat") if request.context else "chat"
    )

    if result["risk_level"] in ["red", "critical"]:
        await audit_logger.record_security_event(
            trace_id=result["trace_id"],
            event_type="INJECTION_DETECTED",
            risk_level=result["risk_level"],
            layer="L2",
            details={"rules_triggered": result["rules_triggered"]}
        )

    return result