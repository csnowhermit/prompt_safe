import re
from typing import Dict, Any, Optional, List

from app.config import settings


class AgentSafeWrapperService:
    def __init__(self):
        self.tool_registry = {
            "query_order_status": {
                "auth_level": "public",
                "params": [
                    {"name": "order_id", "type": "string", "pattern": "^ORD-[A-Z0-9]{10}$", "max_length": 20}
                ],
                "rate_limit": {"rate": 10, "per": "minute"},
                "requires_approval": False
            },
            "issue_refund": {
                "auth_level": "restricted",
                "params": [
                    {"name": "order_id", "type": "string", "pattern": "^ORD-[A-Z0-9]{10}$"},
                    {"name": "amount", "type": "float", "min": 0.01, "max": 99999.99},
                    {"name": "reason", "type": "string", "max_length": 200}
                ],
                "rate_limit": {"rate": 5, "per": "hour"},
                "requires_approval": True,
                "approval_timeout": 300
            },
            "update_model_config": {
                "auth_level": "admin",
                "params": [
                    {"name": "config_key", "type": "string", "allowed_values": ["temperature", "max_tokens"]},
                    {"name": "config_value", "type": "string", "max_length": 50}
                ],
                "rate_limit": {"rate": 2, "per": "day"},
                "requires_approval": True,
                "requires_mfa": True
            }
        }

        self.forbidden_patterns = [
            r"DROP\s+TABLE", r"DELETE\s+FROM", r"INSERT\s+INTO", r"UPDATE\s+\w+",
            r"rm\s+-rf", r"eval\(", r"exec\(", r"system\(",
            r"os\.system", r"subprocess", r"<script>", r"javascript:"
        ]

        self.max_tools_per_turn = 5
        self.max_total_calls = 20

    async def execute(self, tool_name: str, params: Dict[str, Any], user_context: Dict) -> Dict[str, Any]:
        tool = self.tool_registry.get(tool_name)
        if not tool:
            return {"success": False, "error": "TOOL_NOT_FOUND"}

        for key, val in params.items():
            if isinstance(val, str):
                for pattern in self.forbidden_patterns:
                    if re.search(pattern, val, re.IGNORECASE):
                        return {"success": False, "error": "FORBIDDEN_PATTERN_IN_PARAMS"}

        validation_errors = self._validate_params(params, tool.get("params", []))
        if validation_errors:
            return {"success": False, "error": "PARAM_VALIDATION_FAILED", "details": validation_errors}

        if not self._check_permission(user_context.get("role", "end_user"), tool.get("auth_level", "public")):
            return {"success": False, "error": "PERMISSION_DENIED"}

        if tool.get("requires_approval", False):
            return {"success": False, "error": "APPROVAL_REQUIRED", "approval_timeout": tool.get("approval_timeout", 300)}

        simulated_result = {
            "tool": tool_name,
            "params": params,
            "timestamp": "2026-07-15T10:30:00Z",
            "data": {"message": f"工具 {tool_name} 执行成功"}
        }

        return {"success": True, "result": simulated_result}

    def _validate_params(self, params: Dict[str, Any], param_schema: List[Dict]) -> List[str]:
        errors = []
        for param_def in param_schema:
            name = param_def["name"]
            value = params.get(name)

            if value is None:
                errors.append(f"参数 {name} 不能为空")
                continue

            if param_def["type"] == "string":
                if not isinstance(value, str):
                    errors.append(f"参数 {name} 必须是字符串类型")
                if "max_length" in param_def and len(value) > param_def["max_length"]:
                    errors.append(f"参数 {name} 长度超过限制")
                if "pattern" in param_def and not re.match(param_def["pattern"], value):
                    errors.append(f"参数 {name} 格式不正确")
            elif param_def["type"] == "float":
                try:
                    float_value = float(value)
                    if "min" in param_def and float_value < param_def["min"]:
                        errors.append(f"参数 {name} 小于最小值")
                    if "max" in param_def and float_value > param_def["max"]:
                        errors.append(f"参数 {name} 大于最大值")
                except ValueError:
                    errors.append(f"参数 {name} 必须是数字类型")

        return errors

    def _check_permission(self, user_role: str, required_level: str) -> bool:
        role_permissions = {
            "end_user": ["public"],
            "employee": ["public", "employee", "restricted"],
            "admin": ["public", "employee", "restricted", "admin"],
            "agent": ["public", "employee"]
        }
        return required_level in role_permissions.get(user_role, [])

    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        return self.tool_registry.get(tool_name)

    def list_tools(self) -> List[Dict]:
        return [{"name": name, **info} for name, info in self.tool_registry.items()]