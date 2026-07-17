from fastapi import APIRouter

from app.schemas.output_guard import OutputGuardRequest, OutputGuardResponse
from app.services.output_guard import OutputGuardService
from app.services.audit_logger import AuditLoggerService

router = APIRouter()

output_guard = OutputGuardService()
audit_logger = AuditLoggerService()


@router.post("/check", response_model=OutputGuardResponse)
async def check_output(request: OutputGuardRequest):
    result = await output_guard.check(
        request.raw_output,
        context=request.context or {}
    )

    if result["decision"] == "block":
        await audit_logger.record_security_event(
            trace_id=request.trace_id,
            event_type="OUTPUT_BLOCKED",
            risk_level="red",
            layer="L5",
            details={"reason": result.get("block_reason", "")}
        )

    return result