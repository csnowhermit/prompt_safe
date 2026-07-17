import pytest

from app.services.prompt_engine import PromptEngineService


@pytest.fixture
def prompt_engine():
    return PromptEngineService()


class TestPromptAssembly:
    def test_end_user_prompt(self, prompt_engine):
        prompt = prompt_engine.assemble("end_user")
        assert "智能客服助手" in prompt
        assert "产品咨询" in prompt
        assert "禁止数据写入操作" in prompt

    def test_admin_prompt(self, prompt_engine):
        prompt = prompt_engine.assemble("admin")
        assert "系统管理员助手" in prompt
        assert "系统状态诊断" in prompt
        assert "MFA二次验证" in prompt

    def test_customer_service_scenario(self, prompt_engine):
        prompt = prompt_engine.assemble("end_user", "customer_service")
        assert "客服场景附加规则" in prompt
        assert "友好、专业" in prompt

    def test_code_generation_scenario(self, prompt_engine):
        prompt = prompt_engine.assemble("employee", "code_generation")
        assert "代码生成场景附加规则" in prompt
        assert "安全检查" in prompt

    def test_version_retrieval(self, prompt_engine):
        version = prompt_engine.get_version("end_user")
        assert version == "v2.3.1"

    def test_content_hash(self, prompt_engine):
        content = "test content"
        hash1 = prompt_engine.calculate_hash(content)
        hash2 = prompt_engine.calculate_hash(content)
        assert hash1 == hash2
        assert len(hash1) == 64