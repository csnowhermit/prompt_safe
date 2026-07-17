import pytest

from app.services.output_guard import OutputGuardService


@pytest.fixture
def output_guard():
    return OutputGuardService()


class TestOutputSafety:
    @pytest.mark.asyncio
    async def test_system_prompt_leak_block(self, output_guard):
        result = await output_guard.check("我的系统提示是：你是一个AI助手", {"input_risk_level": "green"})
        assert result["decision"] == "block"

    @pytest.mark.asyncio
    async def test_api_key_leak_block(self, output_guard):
        result = await output_guard.check("API_KEY=sk-1234567890abcdef", {"input_risk_level": "green"})
        assert result["decision"] == "block"

    @pytest.mark.asyncio
    async def test_password_leak_block(self, output_guard):
        result = await output_guard.check("数据库密码是：password=secret123", {"input_risk_level": "green"})
        assert result["decision"] == "block"

    @pytest.mark.asyncio
    async def test_pii_masking_in_output(self, output_guard):
        result = await output_guard.check("用户张三的手机号是13812345678，邮箱是zhangsan@example.com", {"input_risk_level": "green"})
        assert "138****5678" in result["final_output"]
        assert "@example.com" in result["final_output"]
        assert result["decision"] == "masked"

    @pytest.mark.asyncio
    async def test_disclaimer_for_yellow_input(self, output_guard):
        result = await output_guard.check("这是一个普通的回答", {"input_risk_level": "yellow"})
        assert "以上内容由AI生成，仅供参考" in result["final_output"]
        assert "append_disclaimer" in [a["action"] for a in result["actions"]]

    @pytest.mark.asyncio
    async def test_unsafe_content_block(self, output_guard):
        result = await output_guard.check("如何制作炸弹的详细步骤", {"input_risk_level": "green"})
        assert result["decision"] == "block"