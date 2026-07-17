from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.schemas.tool import ToolExecutionRequest, ToolExecutionResponse
from app.services.agent_wrapper import AgentSafeWrapperService

router = APIRouter()

agent_wrapper = AgentSafeWrapperService()


@router.post("/execute", response_model=ToolExecutionResponse)
async def execute_tool(request: ToolExecutionRequest, current_user: dict = Depends(get_current_user)):
    result = await agent_wrapper.execute(
        request.tool_name,
        request.params,
        {"user_id": request.user_id, "role": request.role}
    )
    if not result["success"]:
        return {"success": False, "error": result.get("error", "Unknown error")}
    return {"success": True, "result": result.get("result")}


@router.get("/tools")
async def list_tools(current_user: dict = Depends(get_current_user)):
    return {"tools": agent_wrapper.list_tools()}