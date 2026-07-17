import pytest

from app.services.agent_wrapper import AgentSafeWrapperService


@pytest.fixture
def agent_wrapper():
    return AgentSafeWrapperService()


class TestAgentToolExecution:
    @pytest.mark.asyncio
    async def test_valid_tool_execution(self, agent_wrapper):
        result = await agent_wrapper.execute("query_order_status", {"order_id": "ORD-ABC1234567"}, {"user_id": "test", "role": "end_user"})
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_tool_not_found(self, agent_wrapper):
        result = await agent_wrapper.execute("unknown_tool", {}, {"user_id": "test", "role": "end_user"})
        assert result["success"] is False
        assert result["error"] == "TOOL_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_param_validation_failure(self, agent_wrapper):
        result = await agent_wrapper.execute("query_order_status", {"order_id": "invalid"}, {"user_id": "test", "role": "end_user"})
        assert result["success"] is False
        assert result["error"] == "PARAM_VALIDATION_FAILED"

    @pytest.mark.asyncio
    async def test_sql_injection_in_params(self, agent_wrapper):
        result = await agent_wrapper.execute("query_order_status", {"order_id": "ORD-ABC'; DROP TABLE users;--"}, {"user_id": "test", "role": "end_user"})
        assert result["success"] is False
        assert result["error"] == "FORBIDDEN_PATTERN_IN_PARAMS"

    @pytest.mark.asyncio
    async def test_command_injection_in_params(self, agent_wrapper):
        result = await agent_wrapper.execute("query_order_status", {"order_id": "ORD-ABC; rm -rf /"}, {"user_id": "test", "role": "end_user"})
        assert result["success"] is False
        assert result["error"] == "FORBIDDEN_PATTERN_IN_PARAMS"

    @pytest.mark.asyncio
    async def test_permission_denied(self, agent_wrapper):
        result = await agent_wrapper.execute("issue_refund", {"order_id": "ORD-ABC1234567", "amount": 100.0, "reason": "test"}, {"user_id": "test", "role": "end_user"})
        assert result["success"] is False
        assert result["error"] == "PERMISSION_DENIED"

    @pytest.mark.asyncio
    async def test_approval_required(self, agent_wrapper):
        result = await agent_wrapper.execute("issue_refund", {"order_id": "ORD-ABC1234567", "amount": 100.0, "reason": "test"}, {"user_id": "test", "role": "employee"})
        assert result["success"] is False
        assert result["error"] == "APPROVAL_REQUIRED"