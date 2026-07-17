import re
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any


@dataclass
class MaskRule:
    rule_id: str
    name: str
    pattern: str
    validator: callable = None
    mask_func: callable = None


@dataclass
class MaskResult:
    masked_text: str
    masked_count: int = 0
    masked_items: List[Dict[str, Any]] = field(default_factory=list)


class MaskEngine:
    def __init__(self):
        self.rules = self._init_rules()
        self.compiled_rules = [(rule, re.compile(rule.pattern)) for rule in self.rules]

    def _init_rules(self) -> List[MaskRule]:
        rules = []

        rules.append(MaskRule(
            rule_id="R01",
            name="身份证号(18位)",
            pattern=r"(?<!\d)[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx](?!\d)",
            mask_func=lambda m: m.group()[:6] + "********" + m.group()[-4:]
        ))

        rules.append(MaskRule(
            rule_id="R02",
            name="身份证号(15位)",
            pattern=r"(?<!\d)[1-9]\d{5}\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}(?!\d)",
            mask_func=lambda m: m.group()[:6] + "******" + m.group()[-3:]
        ))

        rules.append(MaskRule(
            rule_id="R05",
            name="邮箱地址",
            pattern=r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            mask_func=lambda m: m.group()[0] + "***@" + m.group().split("@")[1]
        ))

        rules.append(MaskRule(
            rule_id="R09",
            name="车牌号",
            pattern=r"(?<!\w)[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z][A-HJ-NP-Z0-9]{4,5}[A-HJ-NP-Z0-9挂学警港澳](?!\w)",
            mask_func=lambda m: m.group()[:2] + "****"
        ))

        rules.append(MaskRule(
            rule_id="R14",
            name="军官证号",
            pattern=r"(?<!\w)军字第\d{8}(?!\w)",
            mask_func=lambda m: m.group()[:3] + "******" + m.group()[-2:]
        ))

        rules.append(MaskRule(
            rule_id="R08",
            name="护照号",
            pattern=r"(?<!\w)[A-Za-z]\d{8}(?!\w)",
            mask_func=lambda m: m.group()[:2] + "******"
        ))

        rules.append(MaskRule(
            rule_id="R16",
            name="港澳通行证号",
            pattern=r"(?<!\w)[HM]\d{8}(?!\w)",
            mask_func=lambda m: m.group()[:2] + "******"
        ))

        rules.append(MaskRule(
            rule_id="R17",
            name="台湾通行证号",
            pattern=r"(?<!\w)[TD]\d{8}(?!\w)",
            mask_func=lambda m: m.group()[:2] + "******"
        ))

        rules.append(MaskRule(
            rule_id="R04",
            name="银行卡号",
            pattern=r"(?<!\d)\d{16,19}(?!\d)",
            mask_func=lambda m: m.group()[:4] + "****" + m.group()[-4:]
        ))

        rules.append(MaskRule(
            rule_id="R10",
            name="统一社会信用代码",
            pattern=r"(?<!\w)[0-9A-HJ-NP-Z]{18}(?!\w)",
            mask_func=lambda m: m.group()[:4] + "****" + m.group()[-4:]
        ))

        rules.append(MaskRule(
            rule_id="R03",
            name="手机号",
            pattern=r"(?<!\d)1[3-9]\d{9}(?!\d)",
            mask_func=lambda m: m.group()[:3] + "****" + m.group()[-4:]
        ))

        rules.append(MaskRule(
            rule_id="R13",
            name="设备IMEI号",
            pattern=r"(?<!\d)\d{15}(?!\d)",
            mask_func=lambda m: m.group()[:3] + "***" + m.group()[-3:]
        ))

        rules.append(MaskRule(
            rule_id="R06",
            name="IPv4地址",
            pattern=r"(?<!\w)(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)(?!\w)",
            mask_func=lambda m: ".".join(m.group().split(".")[:2]) + ".*.*"
        ))

        rules.append(MaskRule(
            rule_id="R07",
            name="IPv6地址",
            pattern=r"(?<!\w)(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}(?!\w)",
            mask_func=lambda m: ":".join(m.group().split(":")[:2]) + "::*"
        ))

        rules.append(MaskRule(
            rule_id="R21",
            name="座机号",
            pattern=r"(?<!\d)0\d{2,3}-?\d{7,8}(?!\d)",
            mask_func=lambda m: m.group()[:4] + "****" + m.group()[-4:]
        ))

        rules.append(MaskRule(
            rule_id="R11",
            name="QQ号",
            pattern=r"(?<!\d)[1-9]\d{4,10}(?!\d)",
            mask_func=lambda m: m.group()[:2] + "***" + m.group()[-2:]
        ))

        return rules

    def _validate_id_card_18(self, value: str) -> bool:
        if len(value) != 18:
            return False
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        total = sum(weights[i] * int(value[i]) for i in range(17))
        expected_check = check_codes[total % 11]
        return value[-1].upper() == expected_check

    def _validate_id_card_15(self, value: str) -> bool:
        if len(value) != 15:
            return False
        region_code = int(value[:6])
        return 110000 <= region_code <= 820000

    def _validate_bank_card(self, value: str) -> bool:
        digits = [int(d) for d in value]
        reversed_digits = digits[::-1]
        total = 0
        for i, d in enumerate(reversed_digits):
            if i % 2 == 1:
                d *= 2
                if d > 9:
                    d -= 9
            total += d
        return total % 10 == 0

    async def mask(self, text: str) -> MaskResult:
        all_matches = []

        for rule, compiled_pattern in self.compiled_rules:
            matches = compiled_pattern.finditer(text)
            for match in matches:
                value = match.group()
                
                if rule.validator and not rule.validator(value):
                    continue
                
                all_matches.append({
                    "rule": rule,
                    "start": match.start(),
                    "end": match.end(),
                    "value": value,
                    "match_obj": match
                })

        all_matches.sort(key=lambda x: (x["start"], -(x["end"] - x["start"])))

        processed_ranges = []
        masked_items = []

        for match in all_matches:
            start = match["start"]
            end = match["end"]
            
            is_overlapping = any(
                start < pr_end and end > pr_start
                for pr_start, pr_end in processed_ranges
            )
            if is_overlapping:
                continue
            
            processed_ranges.append((start, end))
            
            masked_value = match["rule"].mask_func(match["match_obj"])
            masked_items.append({
                "rule_id": match["rule"].rule_id,
                "name": match["rule"].name,
                "original": match["value"],
                "masked": masked_value,
                "start": start,
                "end": end
            })

        masked_items.sort(key=lambda x: x["start"])

        masked_text = text
        offset = 0
        for item in masked_items:
            start = item["start"] + offset
            end = item["end"] + offset
            masked_text = masked_text[:start] + item["masked"] + masked_text[end:]
            offset += len(item["masked"]) - (item["end"] - item["start"])

        return MaskResult(
            masked_text=masked_text,
            masked_count=len(masked_items),
            masked_items=masked_items
        )