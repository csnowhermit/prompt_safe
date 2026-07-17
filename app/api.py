from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from app.safety_gateway import SafetyGateway, ChatRequest
from app.safety_checker import SafetyChecker

app = FastAPI(
    title="AI大模型Prompt安全防护系统",
    description="基于语义安全检查与敏感信息脱敏的轻量级防护方案",
    version="2.0.0"
)

gateway = SafetyGateway()
gateway.safety_checker = SafetyChecker(enable_mock=True)


class ChatAPIRequest(BaseModel):
    prompt: str = Field(description="用户的输入文本")
    model: Optional[str] = Field(default=None, description="指定后端大模型")
    config: Optional[Dict[str, Any]] = Field(default=None, description="覆盖默认配置")


class MaskPreviewRequest(BaseModel):
    text: str = Field(description="待脱敏的文本")


class CheckPreviewRequest(BaseModel):
    text: str = Field(description="待安全检查的文本")


@app.post("/api/v1/chat")
async def chat(request: ChatAPIRequest):
    chat_request = ChatRequest(
        prompt=request.prompt,
        model=request.model,
        config=request.config
    )
    response = await gateway.handle_chat_request(chat_request)
    
    if response.code == 400:
        raise HTTPException(status_code=400, detail=response.message)
    if response.code == 403:
        raise HTTPException(status_code=403, detail=response.message)
    if response.code >= 500:
        raise HTTPException(status_code=response.code, detail=response.message)
    
    return response.__dict__


@app.post("/api/v1/mask/preview")
async def mask_preview(request: MaskPreviewRequest):
    result = await gateway.preview_mask(request.text)
    return {"code": 0, "message": "success", "data": result}


@app.post("/api/v1/check/preview")
async def check_preview(request: CheckPreviewRequest):
    result = await gateway.preview_check(request.text)
    return {"code": 0, "message": "success", "data": result}


@app.get("/health")
async def health():
    result = await gateway.health_check()
    return {"code": 0, "message": "success", "data": result}


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")