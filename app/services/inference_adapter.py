import time
from typing import Optional, Dict, Any

from app.config import settings


class InferenceAdapterService:
    def __init__(self):
        self.stop_sequences = [
            "【系统提示",
            "system prompt:",
            "System Prompt:",
            "API_KEY",
            "password=",
            "<!-- SECRET -->",
            "Bearer eyJ",
            "sk-"
        ]

        self.default_params = {
            "temperature": 0.3,
            "top_p": 0.9,
            "max_tokens": 512,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        }

        self.scenario_params = {
            "customer_service": {"temperature": 0.3, "max_tokens": 512},
            "code_generation": {"temperature": 0.2, "max_tokens": 1024},
            "creative_writing": {"temperature": 0.7, "max_tokens": 2048},
            "rag_qa": {"temperature": 0.2, "max_tokens": 512}
        }

    def get_params(self, scenario: str = None) -> Dict[str, Any]:
        params = self.default_params.copy()
        if scenario and scenario in self.scenario_params:
            params.update(self.scenario_params[scenario])
        return params

    def truncate_by_stop_sequence(self, text: str) -> str:
        min_index = len(text)
        for seq in self.stop_sequences:
            idx = text.find(seq)
            if idx != -1 and idx < min_index:
                min_index = idx
        if min_index < len(text):
            return text[:min_index]
        return text

    async def infer(self, prompt: str, scenario: str = None,
                    params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        start_time = time.time()

        if params is None:
            params = self.get_params(scenario)

        max_tokens = params.get("max_tokens", 512)

        simulated_response = f"这是针对您的请求的模拟响应。\n\n用户输入: {prompt[:50]}..."
        truncated_response = self.truncate_by_stop_sequence(simulated_response)

        actual_length = len(truncated_response)
        if actual_length > max_tokens * 2:
            truncated_response = truncated_response[:max_tokens * 2] + "..."

        latency_ms = (time.time() - start_time) * 1000

        return {
            "response": truncated_response,
            "latency_ms": latency_ms,
            "params": params,
            "truncated": actual_length > max_tokens * 2,
            "stop_sequence_hit": truncated_response != simulated_response
        }

    async def dual_model_inference(self, prompt: str, scenario: str = None) -> Dict[str, Any]:
        main_result = await self.infer(prompt, scenario)

        safety_prompt = f"""请判断以下内容是否安全：
{prompt}

请回答：安全 或 不安全"""
        safety_result = await self.infer(safety_prompt, scenario)

        if "不安全" in safety_result["response"]:
            return {
                "response": "",
                "latency_ms": main_result["latency_ms"] + safety_result["latency_ms"],
                "blocked": True,
                "reason": "SAFETY_MODEL_REJECTED"
            }

        return {
            "response": main_result["response"],
            "latency_ms": main_result["latency_ms"] + safety_result["latency_ms"],
            "blocked": False,
            "safety_checked": True
        }