import pytest
from app.mask_engine import MaskEngine


@pytest.fixture
def mask_engine():
    return MaskEngine()


@pytest.mark.asyncio
async def test_mask_id_card_18(mask_engine):
    text = "我的身份证号是110101199003077755"
    result = await mask_engine.mask(text)
    assert "110101********7755" in result.masked_text
    assert result.masked_count >= 1


@pytest.mark.asyncio
async def test_mask_id_card_15(mask_engine):
    text = "旧身份证号：110101800101123"
    result = await mask_engine.mask(text)
    assert result.masked_count >= 1


@pytest.mark.asyncio
async def test_mask_phone(mask_engine):
    text = "联系电话：13812345678"
    result = await mask_engine.mask(text)
    assert "138****5678" in result.masked_text
    assert result.masked_count == 1


@pytest.mark.asyncio
async def test_mask_bank_card(mask_engine):
    text = "银行卡号：6222021234567890188"
    result = await mask_engine.mask(text)
    assert "6222****0188" in result.masked_text
    assert result.masked_count == 1


@pytest.mark.asyncio
async def test_mask_email(mask_engine):
    text = "邮箱：test@example.com"
    result = await mask_engine.mask(text)
    assert "t***@example.com" in result.masked_text
    assert result.masked_count == 1


@pytest.mark.asyncio
async def test_mask_ipv4(mask_engine):
    text = "服务器IP：192.168.1.100"
    result = await mask_engine.mask(text)
    assert "192.168.*.*" in result.masked_text
    assert result.masked_count == 1


@pytest.mark.asyncio
async def test_mask_car_plate(mask_engine):
    text = "车牌号：京A12345"
    result = await mask_engine.mask(text)
    assert "京A****" in result.masked_text
    assert result.masked_count == 1


@pytest.mark.asyncio
async def test_mask_multiple_types(mask_engine):
    text = "手机号13812345678，身份证110101199003077755，邮箱test@example.com"
    result = await mask_engine.mask(text)
    assert result.masked_count == 3
    assert "138****5678" in result.masked_text
    assert "110101********7755" in result.masked_text
    assert "t***@example.com" in result.masked_text


@pytest.mark.asyncio
async def test_mask_no_sensitive_info(mask_engine):
    text = "今天天气很好，我想去公园散步"
    result = await mask_engine.mask(text)
    assert result.masked_count == 0
    assert result.masked_text == text