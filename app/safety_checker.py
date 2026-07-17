import asyncio
from dataclasses import dataclass
from typing import Optional

from app.config import settings
from app.logger import logger


@dataclass
class SafetyCheckResult:
    is_safe: bool
    confidence: float
    label: str
    action: str


class SafetyChecker:
    def __init__(self, enable_mock=False):
        self.model = None
        self.tokenizer = None
        self._model_loaded = False
        self._load_future = None
        self._enable_mock = enable_mock
        self._unsafe_patterns = [
            r"忽略.*指令",
            r"绕过.*限制",
            r"移除.*限制",
            r"没有.*限制",
            r"打破.*规则",
            r"DAN",
            r"Do Anything Now",
            r"忽略之前",
            r"无视.*规则",
            r"越狱",
            r"注入",
        ]

    async def _load_model(self):
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch

            logger.info(f"Loading safety model: {settings.SAFETY_MODEL}")
            self.tokenizer = AutoTokenizer.from_pretrained(settings.SAFETY_MODEL)
            self.model = AutoModelForSequenceClassification.from_pretrained(settings.SAFETY_MODEL)
            
            if torch.cuda.is_available():
                self.model = self.model.cuda()
            else:
                logger.warning("CUDA not available, using CPU for safety model")
            
            self.model.eval()
            self._model_loaded = True
            logger.info("Safety model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load safety model: {e}")
            self._model_loaded = False

    async def check(self, text: str) -> SafetyCheckResult:
        if self._enable_mock:
            import re
            for pattern in self._unsafe_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return SafetyCheckResult(
                        is_safe=False,
                        confidence=0.9,
                        label="unsafe",
                        action="BLOCK"
                    )
            return SafetyCheckResult(
                is_safe=True,
                confidence=0.9,
                label="safe",
                action="PASS"
            )

        if not self._model_loaded:
            if self._load_future is None:
                self._load_future = asyncio.create_task(self._load_model())
            
            try:
                await asyncio.wait_for(self._load_future, timeout=settings.SAFETY_CHECK_TIMEOUT)
            except asyncio.TimeoutError:
                logger.warning("Safety model loading timeout")
                return self._handle_fallback()

        if not self._model_loaded:
            return self._handle_fallback()

        try:
            from transformers import pipeline
            import torch

            pipe = pipeline(
                "text-classification",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1,
                max_length=512,
                truncation=True
            )

            result = pipe(text)[0]
            label = result["label"].lower()
            confidence = result["score"]

            if label == "safe" and confidence >= settings.SAFETY_THRESHOLD:
                return SafetyCheckResult(
                    is_safe=True,
                    confidence=confidence,
                    label=label,
                    action="PASS"
                )
            elif label == "unsafe" and confidence >= settings.SAFETY_THRESHOLD:
                return SafetyCheckResult(
                    is_safe=False,
                    confidence=confidence,
                    label=label,
                    action="BLOCK"
                )
            else:
                return SafetyCheckResult(
                    is_safe=False,
                    confidence=confidence,
                    label=label,
                    action="BLOCK"
                )

        except Exception as e:
            logger.error(f"Safety check failed: {e}")
            return self._handle_fallback()

    def _handle_fallback(self) -> SafetyCheckResult:
        return SafetyCheckResult(
            is_safe=True,
            confidence=0.0,
            label="unknown",
            action="PASS"
        )

    async def is_model_available(self) -> bool:
        if self._model_loaded:
            return True
        if self._load_future is not None:
            try:
                await asyncio.wait_for(self._load_future, timeout=1)
            except asyncio.TimeoutError:
                pass
        return self._model_loaded