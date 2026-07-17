from fastapi import APIRouter, HTTPException

from app.schemas.tool import ToolExecutionRequest, ToolExecutionResponse
from app.services.agent_wrapper import AgentSafeWrapperService

router = APIRouter()

agent_wrapper = AgentSafeWrapperService()


@router.post("/execute", response_model=ToolExecutionResponse)
async def execute_tool(request: ToolExecutionRequest):
    result = await agent_wrapper.execute(
        request.tool_name,
        request.params,
        {"user_id": request.user_id, "role": request.role}
    )
    if not result["success"]:
        return {"success": False, "error": result.get("error", "Unknown error")}
    return {"success": True, "result": result.get("result")}


@router.get("/tools")
async def list_tools():
    return {"tools": agent_wrapper.list_tools()}