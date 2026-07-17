from dataclasses import dataclass, field
from typing import Optional

from app.config import settings
from app.logger import logger
from app.mask_engine import MaskEngine, MaskResult
from app.safety_checker import SafetyChecker, SafetyCheckResult
from app.llm_proxy import LLMProxy


@dataclass
class SafetyInfo:
    input_check: str = "pass"
    output_check: str = "pass"
    input_confidence: float = 0.0
    output_confidence: float = 0.0


@dataclass
class MaskInfo:
    input_masked_count: int = 0
    output_masked_count: int = 0


@dataclass
class ResponseData:
    response: str = ""
    safety: SafetyInfo = field(default_factory=SafetyInfo)
    mask: MaskInfo = field(default_factory=MaskInfo)


@dataclass
class ChatResponse:
    code: int = 0
    message: str = "success"
    data: ResponseData = field(default_factory=ResponseData)


@dataclass
class ChatRequest:
    prompt: str
    model: Optional[str] = None
    config: Optional[dict] = None


class SafetyGateway:
    def __init__(self):
        self.mask_engine = MaskEngine()
        self.safety_checker = SafetyChecker()
        self.llm_proxy = LLMProxy()

    async def handle_chat_request(self, request: ChatRequest) -> ChatResponse:
        text = request.prompt
        config = request.config or {}
        
        enable_mask = config.get("enable_mask", settings.ENABLE_MASK)
        enable_check = config.get("enable_check", settings.ENABLE_CHECK)
        safety_threshold = config.get("safety_threshold", settings.SAFETY_THRESHOLD)

        if not text:
            return ChatResponse(
                code=400,
                message="输入不能为空",
                data=ResponseData(response="输入不能为空")
            )

        if len(text) > settings.MAX_PROMPT_TOKENS:
            return ChatResponse(
                code=400,
                message="输入超出长度限制",
                data=ResponseData(response="输入超出长度限制")
            )

        masked_text = text
        input_mask_count = 0

        if enable_mask:
            mask_result = await self.mask_engine.mask(text)
            masked_text = mask_result.masked_text
            input_mask_count = mask_result.masked_count
            logger.info("input_masked", count=input_mask_count)

        if enable_check:
            check_result = await self.safety_checker.check(masked_text)

            if not check_result.is_safe:
                logger.warning("input_blocked",
                    confidence=check_result.confidence,
                    text_preview=masked_text[:100])
                return ChatResponse(
                    code=403,
                    message="输入内容未通过安全检查",
                    data=ResponseData(
                        response="您的输入包含不安全内容，请修改后重试。",
                        safety=SafetyInfo(
                            input_check="block",
                            input_confidence=check_result.confidence
                        ),
                        mask=MaskInfo(input_masked_count=input_mask_count)
                    )
                )

            input_confidence = check_result.confidence
        else:
            input_confidence = 0.0

        try:
            llm_response = await self.llm_proxy.forward(masked_text, request.model)
        except Exception as e:
            logger.error(f"LLM proxy error: {e}")
            return ChatResponse(
                code=502,
                message="模型服务暂时不可用",
                data=ResponseData(response="模型服务暂时不可用")
            )

        output_confidence = 0.0

        if enable_check:
            output_check = await self.safety_checker.check(llm_response)

            if not output_check.is_safe:
                logger.warning("output_blocked",
                    confidence=output_check.confidence,
                    text_preview=llm_response[:100])
                return ChatResponse(
                    code=403,
                    message="输出内容未通过安全检查",
                    data=ResponseData(
                        response="抱歉，模型生成的回复未通过安全检查，无法返回。",
                        safety=SafetyInfo(
                            input_check="pass",
                            input_confidence=input_confidence,
                            output_check="block",
                            output_confidence=output_check.confidence
                        ),
                        mask=MaskInfo(input_masked_count=input_mask_count)
                    )
                )

            output_confidence = output_check.confidence

        final_response = llm_response
        output_mask_count = 0

        if enable_mask:
            output_mask_result = await self.mask_engine.mask(llm_response)
            final_response = output_mask_result.masked_text
            output_mask_count = output_mask_result.masked_count

        return ChatResponse(
            code=0,
            message="success",
            data=ResponseData(
                response=final_response,
                safety=SafetyInfo(
                    input_check="pass",
                    input_confidence=input_confidence,
                    output_check="pass",
                    output_confidence=output_confidence
                ),
                mask=MaskInfo(
                    input_masked_count=input_mask_count,
                    output_masked_count=output_mask_count
                )
            )
        )

    async def preview_mask(self, text: str) -> dict:
        result = await self.mask_engine.mask(text)
        return {
            "original": text,
            "masked": result.masked_text,
            "count": result.masked_count,
            "items": result.masked_items
        }

    async def preview_check(self, text: str) -> dict:
        result = await self.safety_checker.check(text)
        return {
            "is_safe": result.is_safe,
            "confidence": result.confidence,
            "label": result.label,
            "action": result.action
        }

    async def health_check(self) -> dict:
        model_available = await self.safety_checker.is_model_available()
        return {
            "status": "healthy" if model_available else "degraded",
            "model_available": model_available,
            "version": "2.0.0"
        }