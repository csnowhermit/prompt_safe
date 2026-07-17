import re
import time
import base64
import hashlib
from typing import List, Tuple
from uuid import UUID

from app.config import settings
from app.core.security_context import (
    SecurityContext, RiskLevel, DecisionType, IntentType,
    ClassificationResult, RuleMatch, InputInfo, ProcessingMetrics
)


class InjectionPatternMatcher:
    def __init__(self):
        self.patterns = {
            "instruction_override": [
                re.compile(r"(?i)(ignore|forget|disregard)\s+(all\s+)?(previous|above|prior)", re.IGNORECASE),
                re.compile(r"(忽略|忘记)(以上|前面|之前).*(指令|规则|内容|对话)", re.IGNORECASE),
                re.compile(r"(無視|むし).*(指示|命令)", re.IGNORECASE),
                re.compile(r"(Игнорируй|Забудь).*(инструкции|правила)", re.IGNORECASE),
            ],
            "roleplay_induction": [
                re.compile(r"(?i)(you\s+are\s+now|act\s+as|pretend\s+to\s+be)", re.IGNORECASE),
                re.compile(r"(假设你是|请你扮演|你现在是一个)", re.IGNORECASE),
                re.compile(r"(?i)(roleplay|developer\s+mode|god\s+mode|dan\s+mode)", re.IGNORECASE),
            ],
            "info_extraction": [
                re.compile(r"(?i)(output|show|reveal|repeat|print).{0,20}(system\s+)?prompt", re.IGNORECASE),
                re.compile(r"(?i)(what\s+is|tell\s+me|show\s+me).{0,20}(system\s+prompt|instructions)", re.IGNORECASE),
                re.compile(r"你的(系统提示|指令|预设|prompt).*是?[什么|哪些]", re.IGNORECASE),
            ],
            "social_engineering": [
                re.compile(r"(我是你的)?(开发者|管理员|创建者|所有者)", re.IGNORECASE),
                re.compile(r"(这是)(CEO|老板|领导|上级).*(要求|指令|命令)", re.IGNORECASE),
                re.compile(r"(紧急情况|系统被入侵|安全漏洞)", re.IGNORECASE),
            ],
            "privilege_escalation": [
                re.compile(r"(?i)(give\s+me|grant\s+me|make\s+me).{0,20}(admin|root|superuser)", re.IGNORECASE),
                re.compile(r"(给我|赋予我|提升).*(管理员|超级|最高).*(权限|级别)", re.IGNORECASE),
                re.compile(r"(?i)(sudo|chmod|chown).*(root|admin)", re.IGNORECASE),
            ],
        }

    def scan(self, text: str) -> List[RuleMatch]:
        matches = []
        for category, patterns in self.patterns.items():
            for idx, pattern in enumerate(patterns):
                found = pattern.search(text)
                if found:
                    matches.append(RuleMatch(
                        rule_id=f"L2-PAT-{category[:3].upper()}-{idx:03d}",
                        match=found.group(0),
                        category=category
                    ))
        return matches


class KeywordMatcher:
    def __init__(self):
        self.keywords = {
            "prompt_injection": [
                "ignore all previous", "forget all", "disregard previous",
                "你现在是", "假设你是", "请你扮演", "你现在是一个",
                "system prompt", "系统提示", "系统指令",
                "DAN mode", "developer mode", "god mode", "jailbreak",
                "output your system", "输出你的", "show me your", "reveal your",
                "忽略以上", "忘记前面", "无视指示",
                "act as dan", "do anything now",
            ],
            "social_engineering": [
                "我是你的开发者", "我是管理员", "这是CEO", "紧急情况", "安全漏洞",
                "配合测试", "输出所有安全规则",
            ],
            "code_injection": [
                "eval(", "exec(", "system(", "subprocess", "os.system",
                "DROP TABLE", "DELETE FROM", "INSERT INTO", "OR 1=1",
                "<script>", "<iframe>", "onload=", "javascript:",
            ],
        }

    def scan(self, text: str) -> List[RuleMatch]:
        matches = []
        for category, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    matches.append(RuleMatch(
                        rule_id=f"L2-KW-{category[:3].upper()}-{keywords.index(keyword):03d}",
                        match=keyword,
                        category=category
                    ))
        return matches


class ObfuscationDetector:
    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold

    def detect(self, text: str) -> float:
        score = 0.0
        checks = []

        checks.append(self._check_base64(text))
        checks.append(self._check_hex(text))
        checks.append(self._check_unicode_escape(text))
        checks.append(self._check_special_chars(text))

        if checks:
            score = max(checks)

        return score

    def _check_base64(self, text: str) -> float:
        base64_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")
        text_chars = [c for c in text if c in base64_chars]
        if len(text) == 0:
            return 0.0
        ratio = len(text_chars) / len(text)
        
        if re.match(r"^\d+$", text):
            return 0.0
        
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        if len(chinese_chars) > 0 and ratio < 0.95:
            return 0.0
        
        return ratio if ratio > 0.8 else 0.0

    def _check_hex(self, text: str) -> float:
        hex_pattern = re.compile(r"\\x[0-9a-fA-F]{2}")
        matches = hex_pattern.findall(text)
        return len(matches) / max(len(text) / 4, 1) if matches else 0.0

    def _check_unicode_escape(self, text: str) -> float:
        unicode_pattern = re.compile(r"\\u[0-9a-fA-F]{4}")
        matches = unicode_pattern.findall(text)
        return len(matches) / max(len(text) / 6, 1) if matches else 0.0

    def _check_special_chars(self, text: str) -> float:
        special_chars = set("!@#$%^&*()_+-=[]{}|;:,.<>?/~`\\")
        count = sum(1 for c in text if c in special_chars)
        if len(text) == 0:
            return 0.0
        ratio = count / len(text)
        return ratio if ratio > 0.3 else 0.0


class SafetyClassifier:
    def __init__(self):
        pass

    def classify(self, text: str) -> ClassificationResult:
        text_lower = text.lower()

        if not text.strip():
            return ClassificationResult(intent=IntentType.NORMAL_QUERY, confidence=0.90)

        jailbreak_patterns = [
            "dan mode", "developer mode", "god mode", "jailbreak",
            "ignore all", "forget all", "假设你是一个没有限制的",
            "你现在是一个没有限制的", "无限制模式", "越狱模式",
            "act as dan", "do anything now",
        ]
        for pattern in jailbreak_patterns:
            if pattern in text_lower:
                return ClassificationResult(intent=IntentType.JAILBREAK, confidence=0.95)

        info_extract_patterns = [
            "system prompt", "系统提示", "系统指令", "输出你的",
            "show me your instructions", "reveal your prompt",
            "我是你的开发者", "配合测试", "输出所有安全规则",
        ]
        for pattern in info_extract_patterns:
            if pattern in text_lower:
                return ClassificationResult(intent=IntentType.INFO_EXTRACT, confidence=0.90)

        illegal_patterns = [
            "制作炸弹", "黑客攻击", "勒索病毒", "钓鱼邮件",
            "色情", "暴力", "政治敏感", "欺诈",
        ]
        for pattern in illegal_patterns:
            if pattern in text_lower:
                return ClassificationResult(intent=IntentType.ILLEGAL, confidence=0.85)

        code_injection_patterns = [
            "eval(", "exec(", "os.system", "subprocess",
            "DROP TABLE", "DELETE FROM", "<script>",
            "OR 1=1", "OR '1'='1'",
        ]
        for pattern in code_injection_patterns:
            if pattern in text_lower:
                return ClassificationResult(intent=IntentType.CODE_INJECTION, confidence=0.90)

        if "' OR '1'='1'" in text:
            return ClassificationResult(intent=IntentType.CODE_INJECTION, confidence=0.95)

        safe_patterns = [
            "帮我", "请帮我", "如何", "什么是", "查询",
            "订单", "产品", "代码", "写一个", "总结",
            "超时时间", "默认是多少",
            "忽略我上一条", "错别字",
        ]
        if any(pattern in text_lower for pattern in safe_patterns):
            return ClassificationResult(intent=IntentType.NORMAL_QUERY, confidence=0.85)

        return ClassificationResult(intent=IntentType.UNSURE, confidence=0.50)


class PIICleaner:
    def __init__(self):
        self.patterns = [
            (re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)"), lambda m: m.group(0)[:3] + "***********" + m.group(0)[-4:]),
            (re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), lambda m: m.group(0)[:3] + "****" + m.group(0)[-4:]),
            (re.compile(r"[\w.-]+@[\w.-]+\.\w+"), lambda m: self._mask_email(m.group(0))),
            (re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"), lambda m: self._mask_ip(m.group(0))),
            (re.compile(r"[0-9A-Fa-f]{2}(:|-)[0-9A-Fa-f]{2}(:|-)[0-9A-Fa-f]{2}(:|-)[0-9A-Fa-f]{2}(:|-)[0-9A-Fa-f]{2}(:|-)[0-9A-Fa-f]{2}"),
             lambda m: m.group(0)[:5] + ":**:****"),
            (re.compile(r"(?<!\d)\d{16}(?!\d)"), lambda m: m.group(0)[:4] + "****" + m.group(0)[-4:]),
        ]

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
        for pattern, replacer in self.patterns:
            text = pattern.sub(replacer, text)
        return text


class InputGuardService:
    def __init__(self):
        self.pattern_matcher = InjectionPatternMatcher()
        self.keyword_matcher = KeywordMatcher()
        self.obfuscation_detector = ObfuscationDetector(settings.obfuscation_threshold)
        self.safety_classifier = SafetyClassifier()
        self.pii_cleaner = PIICleaner()

    async def process(self, text: str, user_id: str, role: str,
                      trace_id: UUID = None, session_id: UUID = None,
                      mode: str = "chat") -> dict:
        start_time = time.time()

        ctx = SecurityContext()
        if trace_id:
            ctx.trace_id = trace_id
        if session_id:
            ctx.session_id = session_id
        ctx.user_id = user_id
        ctx.role = role

        ctx.input = InputInfo(raw_text=text, char_count=len(text))

        if len(text) > settings.max_input_chars:
            return self._build_response(ctx, DecisionType.BLOCK, "INPUT_TOO_LONG")

        obfuscation_score = self.obfuscation_detector.detect(text)
        if obfuscation_score > settings.obfuscation_threshold:
            ctx.upgrade_risk(RiskLevel.RED)
            return self._build_response(ctx, DecisionType.BLOCK, "OBFUSCATION_DETECTED")

        keyword_hits = self.keyword_matcher.scan(text)
        pattern_hits = self.pattern_matcher.scan(text)

        for hit in keyword_hits + pattern_hits:
            ctx.add_rule(hit)

        classification = self.safety_classifier.classify(text)

        if classification.intent in [IntentType.JAILBREAK, IntentType.INFO_EXTRACT,
                                     IntentType.ILLEGAL, IntentType.CODE_INJECTION]:
            ctx.upgrade_risk(RiskLevel.RED)
            return self._build_response(ctx, DecisionType.BLOCK, f"{classification.intent.value.upper()}_DETECTED")

        if classification.confidence < 0.60:
            ctx.upgrade_risk(RiskLevel.YELLOW)

        if keyword_hits or pattern_hits:
            ctx.upgrade_risk(RiskLevel.YELLOW)

        sanitized = self.pii_cleaner.mask(text)
        normalized = self._normalize(sanitized)

        processing_ms = (time.time() - start_time) * 1000

        return {
            "trace_id": str(ctx.trace_id),
            "risk_level": ctx.risk_level.value,
            "decision": DecisionType.ALLOW.value,
            "sanitized_text": normalized,
            "rules_triggered": [
                {"rule_id": r.rule_id, "match": r.match, "category": r.category}
                for r in ctx.rules_triggered
            ],
            "classification": {
                "intent": classification.intent.value,
                "confidence": classification.confidence
            },
            "metrics": {
                "char_count": len(text),
                "obfuscation_score": obfuscation_score,
                "processing_ms": processing_ms
            }
        }

    def _normalize(self, text: str) -> str:
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        text = text.encode("utf-8", errors="replace").decode("utf-8")
        return text

    def _build_response(self, ctx: SecurityContext, decision: DecisionType, reason: str) -> dict:
        return {
            "trace_id": str(ctx.trace_id),
            "risk_level": ctx.risk_level.value,
            "decision": decision.value,
            "sanitized_text": "",
            "rules_triggered": [
                {"rule_id": r.rule_id, "match": r.match, "category": r.category}
                for r in ctx.rules_triggered
            ],
            "classification": {
                "intent": IntentType.UNSURE.value,
                "confidence": 0.0
            },
            "metrics": {
                "char_count": ctx.input.char_count,
                "obfuscation_score": 0.0,
                "processing_ms": 0.0
            },
            "block_reason": reason
        }