from __future__ import annotations

import calendar
import re
from datetime import date

from runner.schemas import TaskTemplate

DATE_FIELDS = {"book_flight": "date", "change_flight": "new_date", "get_weather": "date"}
MONTHS = {name.lower(): i for names in (calendar.month_name, calendar.month_abbr) for i, name in enumerate(names) if name}
MONTHS["sept"] = 9
MONTH_PATTERN = "|".join(sorted(MONTHS, key=len, reverse=True))
EN_DATE = re.compile(rf"\b({MONTH_PATTERN})\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?\b(?:,?\s+(\d{{4}})\b)?", re.I)
ZH_DATE = re.compile(r"(?:(\d{4})\s*年\s*)?(\d{1,2})\s*月\s*(\d{1,2})\s*[日号]?")
ISO_DATE = re.compile(r"(?<![\w-])(\d{4})[-/](\d{1,2})[-/](\d{1,2})(?!\d|-[\d])", re.ASCII)
ASK = re.compile(
    r"[?？]|\b(?:please\s+(?:provide|tell|give|share|specify|confirm|send|supply|enter|let me know)|"
    r"(?:could|can|would|will) you|(?:i|we)(?:['’]ll)? (?:need|require|must have)|(?:what|which|when|where)\s+(?:is|are|would|do)|"
    r"let me know|would (?:also )?be helpful)\b|请.{0,8}(?:提供|告诉|告知|说明|确认|补充|给出|给我|描述|选择)|"
    r"(?:需要|还缺).{0,12}(?:信息|日期|城市|语言|订单|编号|文本|提供)|(?:哪[个一年天日种]|什么|多少|几月几[日号])",
    re.I,
)
SLOTS = {
    "booking_id": r"\b(?:booking|reservation|confirmation|pnr)\b.{0,30}\b(?:id|number|ref(?:erence)?|code)\b|\bpnr\b|(?:预[订约定]|订[票单]|航班).{0,12}(?:编号|号|标识|编码|id)|(?:预订|订座)记录",
    "category": r"\b(?:category|type of (?:issue|ticket))\b|类别|分类|类型",
    "city": r"\b(?:city|town|location|place|region)\b|城市|地点|地区|位置|哪里|哪儿",
    "date": r"\b(?:date|year|day|when|month)\b|日期|哪[年天日]|哪一年|时间|年份|几月几|几号|哪一日",
    "description": r"\b(?:description|describe|details? (?:about|of) (?:the |your )?(?:issue|problem)|issue details|what (?:issue|problem)|what.+issue|what happened)\b|问题描述|描述|具体问题|问题详情|情况|发生了什么",
    "destination": r"\b(?:destination|arriv\w+|where (?:are|will|do) you (?:going|go|fly|flying|travel))\b|目的地|到达|抵达|飞往|到哪|去哪",
    "entity_type": r"\b(?:entity type|record type|type of (?:entity|record)|(?:customer|employee|order|product|ticket) or)\b|实体类型|记录类型|数据类型|哪种记录|(?:哪种|什么)(?:的)?类型",
    "flight_no": r"\bflight\s+(?:number|no\.?|code|id)\b|航班(?:编号|号)|班次",
    "new_date": r"\b(?:date|year|day|when|month)\b|日期|哪[年天日]|哪一年|时间|年份|几月几|几号|哪一日",
    "order_id": r"\border\s+(?:id|number|ref(?:erence)?|identifier|no\.?)\b|\bwhich order\b|订单.{0,5}(?:编号|号|标识|id)|哪[个一笔张条]订单",
    "origin": r"\b(?:origin|departure|departing|depart|from which|where (?:from|are you (?:departing|leaving)))\b|出发|起点|始发|从哪",
    "priority": r"\b(?:priority|urgency|urgent|low, medium)\b|优先|紧急",
    "query": r"\b(?:query|topic|keywords?|subject|details?|identifier|\w+ id|search (?:for|terms)|looking for|(?:which|what) (?:records?|information|document|policy|procedure|customer|process|department)|name)\b|查询内容|关键词|主题|话题|具体|详情|名称|名字|编号|哪个部门|(?:订单|客户|工单)\s*id|什么(?:信息|内容|话题)|(?:搜索|查找|查).{0,6}什么",
    "status": r"\b(?:status|state)\b|状态",
    "target_lang": r"\blanguage\b|语言|语种|翻成.{0,4}语|译成.{0,4}语",
    "text": r"\b(?:text|sentence|phrase|passage|content|original|words)\b|原文|文本|句[子话]|内容|文字",
    "user_id": r"\b(?:user|customer|account).{0,18}\b(?:id|identifier|username|email|number)\b|\b(?:user ID|username)\b|用户.{0,10}(?:id|标识|编号|名|账号)|邮箱|受影响用户",
}

# These generated utterances replace the seed request but used to inherit its slots.
GENERATED_FIELDS = {
    ("change_flight", "帮我把机票改签一下"): {"booking_id", "new_date"},
    ("change_flight", "please change my flight booking"): {"booking_id", "new_date"},
    ("create_support_ticket", "帮我开一个这个用户的支持工单"): {"user_id", "category", "priority", "description"},
    ("create_support_ticket", "open a support ticket for this user"): {"user_id", "category", "priority", "description"},
    ("get_weather", "帮我查一下那天的天气"): {"city", "date"},
    ("get_weather", "can you check the weather for me"): {"city"},
    ("update_order", "把这个订单状态改一下"): {"order_id", "status"},
    ("update_order", "update this order status for me"): {"order_id", "status"},
}


def has_month_day_without_year(text: str, target: date) -> bool:
    explicit = [(int(m), int(d)) for _, m, d in ISO_DATE.findall(text)]
    chinese = [(int(m), int(d), y) for y, m, d in ZH_DATE.findall(text)]
    english = [(MONTHS[m.lower()], int(d), y) for m, d, y in EN_DATE.findall(text)]
    month_day = (target.month, target.day)
    if month_day in explicit or any((m, d) == month_day and y for m, d, y in chinese + english):
        return False
    return any((m, d) == month_day for m, d, _ in chinese + english)


def expected_clarification(task: TaskTemplate, variant_name: str) -> tuple[set[str], str | None]:
    variant = task.variants[variant_name]
    fields = set(variant.clarification_fields) if variant.need_clarification else set()
    if variant.need_clarification and not task.dialog_context:
        text = variant.utterance.strip().rstrip(".。?？").casefold()
        fields = set(GENERATED_FIELDS.get((task.gold_tool, text), fields))
        if task.gold_tool == "book_flight" and task.gold_params.get("flight_no"):
            flight = task.gold_params["flight_no"].casefold()
            if text in {f"帮我订 {flight} 的航班", f"book {flight} for me"}:
                fields = {"date", "origin", "destination"}
        if task.gold_tool == "translate_text" and re.search(r"\b(?:this|that)\s+sentence\b|这(?:一)?句|那(?:一)?句", text):
            fields.update(("text", "target_lang"))
    if task.gold_tool == "search_database" and "entity_type" in fields:
        entity_type = str(task.gold_params["entity_type"])
        if re.search(rf"\b{re.escape(entity_type)}\b", variant.utterance, re.I):
            fields.remove("entity_type")
    field = DATE_FIELDS.get(task.gold_tool)
    if field and task.gold_params.get(field):
        text = "\n".join([*(message["content"] for message in task.dialog_context), variant.utterance])
        try:
            target = date.fromisoformat(task.gold_params[field])
        except ValueError:
            return fields, None
        if has_month_day_without_year(text, target):
            fields.add(field)
            return fields, field
    return fields, None


def missing_reply_fields(reply: str, fields: set[str], year_field: str | None) -> set[str]:
    requests = []
    list_intro = False
    for line in reply.splitlines():
        line = line.strip().replace("**", "").replace("`", "")
        if not line:
            continue
        if list_intro and re.match(r"(?:[-*•]\s+|\d+[.)、]\s*)", line):
            requests.append(line)
            continue
        list_intro = False
        for sentence in re.split(r"(?<=[。！？])|(?<=[.?!])\s+", line):
            if ASK.search(sentence):
                requests.append(sentence)
                list_intro = sentence.endswith((":", "："))
    prompt = "\n".join(requests)
    missing = set()
    for field in fields:
        if field == year_field:
            pattern = r"\byear\b|年份|哪[一年]|哪一年的|哪年|什么年|yyyy(?:[-/]mm[-/]dd)?|完整日期|日期.{0,10}年"
        else:
            pattern = SLOTS.get(field, rf"\b{re.escape(field.replace('_', ' '))}\b")
        if not re.search(pattern, prompt, re.I):
            missing.add(field)
    return missing
