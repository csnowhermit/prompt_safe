import re
import time
from typing import List

from app.config import settings
from app.core.security_context import OutputDecision, RiskLevel


class OutputRuleMatcher:
    def __init__(self):
        self.rules = [
            {"pattern": re.compile(r"【系统提示"), "severity": "critical", "reason": "SYSTEM_PROMPT_LEAK"},
            {"pattern": re.compile(r"system prompt:", re.IGNORECASE), "severity": "critical", "reason": "SYSTEM_PROMPT_LEAK"},
            {"pattern": re.compile(r"System Prompt:", re.IGNORECASE), "severity": "critical", "reason": "SYSTEM_PROMPT_LEAK"},
            {"pattern": re.compile(r"我的系统提示是"), "severity": "critical", "reason": "SYSTEM_PROMPT_LEAK"},
            {"pattern": re.compile(r"系统提示词"), "severity": "critical", "reason": "SYSTEM_PROMPT_LEAK"},
            {"pattern": re.compile(r"API_KEY"), "severity": "critical", "reason": "API_KEY_LEAK"},
            {"pattern": re.compile(r"password="), "severity": "critical", "reason": "PASSWORD_LEAK"},
            {"pattern": re.compile(r"<!-- SECRET -->"), "severity": "critical", "reason": "SECRET_LEAK"},
            {"pattern": re.compile(r"Bearer\s+eyJ"), "severity": "critical", "reason": "JWT_LEAK"},
            {"pattern": re.compile(r"sk-[a-zA-Z0-9]+"), "severity": "critical", "reason": "API_KEY_LEAK"},
        ]

    def match(self, text: str) -> List[dict]:
        matches = []
        for rule in self.rules:
            if rule["pattern"].search(text):
                matches.append(rule)
        return matches


class ContentModerator:
    def __init__(self):
        self.categories = {
            "violence": ["炸弹", "爆炸", "杀人", "攻击", "暴力", "武器", "枪支"],
            "sexual": ["色情", "裸体", "性交", "性暗示", "成人内容"],
            "fraud": ["钓鱼", "诈骗", "勒索", "欺诈", "洗钱"],
            "political": ["政治敏感", "煽动", "颠覆"],
            "hate": ["歧视", "仇恨", "种族", "偏见"],
            "suicide": ["自杀", "自残", "死亡"],
        }

    def check(self, text: str) -> dict:
        text_lower = text.lower()
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return {"is_unsafe": True, "category": category}
        return {"is_unsafe": False, "category": None}


class PIICleaner:
    def __init__(self):
        self.patterns = [
            (re.compile(r"1[3-9]\d{9}"), lambda m: m.group(0)[:3] + "****" + m.group(0)[-4:]),
            (re.compile(r"\d{17}[\dXx]"), lambda m: m.group(0)[:3] + "***********" + m.group(0)[-4:]),
            (re.compile(r"[\w.-]+@[\w.-]+\.\w+"), lambda m: self._mask_email(m.group(0))),
            (re.compile(r"\d{16,19}"), lambda m: m.group(0)[:4] + "****" + m.group(0)[-4:]),
            (re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"), lambda m: self._mask_ip(m.group(0))),
        ]
        self.last_count = 0

    def _mask_email(self, email: str) -> str:
        parts = email.split("@")
        if len(parts) == 2:
            return parts[0][0] + "***@" + parts[1]
        return email

    def _mask_ip(self, ip: str) -> str:
        parts = ip.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.*.*"
        return ip

    def mask(self, text: str) -> str:
        self.last_count = 0
        for pattern, replacer in self.patterns:
            original_count = len(pattern.findall(text))
            text = pattern.sub(replacer, text)
            self.last_count += original_count
        return text


class OutputGuardService:
    def __init__(self):
        self.rule_matcher = OutputRuleMatcher()
        self.content_moderator = ContentModerator()
        self.pii_cleaner = PIICleaner()

    async def check(self, raw_output: str, context: dict = None) -> dict:
        start_time = time.time()

        context = context or {}
        input_risk_level = context.get("input_risk_level", "green")

        rule_matches = self.rule_matcher.match(raw_output)
        for match in rule_matches:
            if match["severity"] == "critical":
                return {
                    "trace_id": context.get("trace_id", ""),
                    "decision": OutputDecision.BLOCK.value,
                    "final_output": "抱歉，我无法协助处理该请求。如有其他问题，欢迎继续咨询。",
                    "actions": [],
                    "block_reason": match["reason"]
                }

        content_check = self.content_moderator.check(raw_output)
        if content_check["is_unsafe"]:
            return {
                "trace_id": context.get("trace_id", ""),
                "decision": OutputDecision.BLOCK.value,
                "final_output": "抱歉，我无法协助处理该请求。如有其他问题，欢迎继续咨询。",
                "actions": [],
                "block_reason": f"UNSAFE_CONTENT:{content_check['category']}"
            }

        masked = self.pii_cleaner.mask(raw_output)
        pii_count = self.pii_cleaner.last_count

        if len(masked) > settings.max_output_chars:
            masked = masked[:settings.max_output_chars] + "...（内容过长已截断）"

        actions = []
        if pii_count > 0:
            actions.append({"action": "pii_mask", "count": pii_count})

        if input_risk_level == "yellow":
            masked += "\n> 以上内容由AI生成，仅供参考。"
            actions.append({"action": "append_disclaimer"})

        decision = OutputDecision.PASS.value
        if pii_count > 0:
            decision = OutputDecision.MASKED.value

        return {
            "trace_id": context.get("trace_id", ""),
            "decision": decision,
            "final_output": masked,
            "actions": actions,
            "block_reason": None
        }