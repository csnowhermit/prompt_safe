from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class RiskLevel(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    CRITICAL = "critical"


class IntentType(str, Enum):
    NORMAL_QUERY = "normal_query"
    JAILBREAK = "jailbreak"
    INFO_EXTRACT = "info_extract"
    ILLEGAL = "illegal"
    CODE_INJECTION = "code_injection"
    UNSURE = "unsure"


class DecisionType(str, Enum):
    ALLOW = "allow"
    FLAG = "flag"
    BLOCK = "block"
    BLOCK_AND_ALERT = "block_and_alert"


class OutputDecision(str, Enum):
    PASS = "pass"
    MASKED = "masked"
    REWRITE = "rewrite"
    BLOCK = "block"


class RoleType(str, Enum):
    END_USER = "end_user"
    EMPLOYEE = "employee"
    ADMIN = "admin"
    AGENT = "agent"


class EventCategory(str, Enum):
    SECURITY = "SECURITY"
    INFERENCE = "INFERENCE"
    SESSION = "SESSION"
    RAG = "RAG"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class InputInfo:
    raw_text: str = ""
    language: str = "zh-CN"
    char_count: int = 0
    has_media: bool = False


@dataclass
class ClassificationResult:
    intent: IntentType
    confidence: float


@dataclass
class RuleMatch:
    rule_id: str
    match: str
    category: str


@dataclass
class ProcessingMetrics:
    char_count: int = 0
    obfuscation_score: float = 0.0
    processing_ms: float = 0.0


@dataclass
class SecurityContext:
    trace_id: UUID = field(default_factory=uuid4)
    session_id: UUID = field(default_factory=uuid4)
    user_id: str = ""
    role: RoleType = RoleType.END_USER
    request_id: str = field(default_factory=lambda: f"req_{uuid4().hex[:8]}")
    risk_level: RiskLevel = RiskLevel.GREEN
    input: InputInfo = field(default_factory=InputInfo)
    rules_triggered: list[RuleMatch] = field(default_factory=list)
    actions_taken: list[str] = field(default_factory=list)
    latency: dict[str, float] = field(default_factory=dict)
    final_status: str = "success"
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def add_rule(self, rule: RuleMatch):
        self.rules_triggered.append(rule)

    def add_action(self, action: str):
        self.actions_taken.append(action)

    def set_latency(self, layer: str, ms: float):
        self.latency[layer] = ms

    def upgrade_risk(self, new_level: RiskLevel):
        levels = [RiskLevel.GREEN, RiskLevel.YELLOW, RiskLevel.RED, RiskLevel.CRITICAL]
        current_idx = levels.index(self.risk_level)
        new_idx = levels.index(new_level)
        if new_idx > current_idx:
            self.risk_level = new_level