import time
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.input_guard import InputGuardService
from app.services.output_guard import OutputGuardService
from app.services.prompt_engine import PromptEngineService
from app.services.session_manager import SessionManagerService
from app.services.inference_adapter import InferenceAdapterService
from app.services.audit_logger import AuditLoggerService

router = APIRouter()

input_guard = InputGuardService()
output_guard = OutputGuardService()
prompt_engine = PromptEngineService()
session_manager = SessionManagerService()
inference_adapter = InferenceAdapterService()
audit_logger = AuditLoggerService()


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    start_time = time.time()

    if not request.session_id:
        request.session_id = await session_manager.create_session(request.user_id, request.role)

    input_result = await input_guard.process(
        request.message,
        request.user_id,
        request.role,
        trace_id=UUID(request.session_id) if request.session_id else None,
        mode=request.mode
    )

    if input_result["decision"] == "block":
        await audit_logger.record_security_event(
            trace_id=input_result["trace_id"],
            event_type="INPUT_BLOCKED",
            risk_level=input_result["risk_level"],
            layer="L2",
            details={"reason": input_result.get("block_reason", "")}
        )
        return ChatResponse(
            session_id=request.session_id,
            response="抱歉，我无法协助处理该请求。如有其他问题，欢迎继续咨询。",
            risk_level=input_result["risk_level"],
            safety_actions=["input_blocked"],
            latency_ms=(time.time() - start_time) * 1000
        )

    system_prompt = prompt_engine.assemble(request.role, request.mode)

    inference_result = await inference_adapter.infer(
        f"{system_prompt}\n\n用户输入: {input_result['sanitized_text']}",
        scenario=request.mode
    )

    output_result = await output_guard.check(
        inference_result["response"],
        context={"input_risk_level": input_result["risk_level"]}
    )

    if output_result["decision"] == "block":
        await audit_logger.record_security_event(
            trace_id=input_result["trace_id"],
            event_type="OUTPUT_BLOCKED",
            risk_level="red",
            layer="L5",
            details={"reason": output_result.get("block_reason", "")}
        )

    await session_manager.add_message(
        request.session_id,
        "user",
        input_result["sanitized_text"],
        risk_level=input_result["risk_level"]
    )
    await session_manager.add_message(
        request.session_id,
        "assistant",
        output_result["final_output"],
        risk_level=input_result["risk_level"]
    )

    safety_actions = []
    if input_result["rules_triggered"]:
        safety_actions.append("rule_triggered")
    if output_result["actions"]:
        safety_actions.extend([a["action"] for a in output_result["actions"]])

    latency_ms = (time.time() - start_time) * 1000

    return ChatResponse(
        session_id=request.session_id,
        response=output_result["final_output"],
        risk_level=input_result["risk_level"],
        safety_actions=safety_actions,
        latency_ms=latency_ms
    )