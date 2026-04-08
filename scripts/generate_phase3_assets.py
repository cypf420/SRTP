from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runner.io_utils import load_tasks
from runner.schemas import TaskTemplate

MAIN_DIR = ROOT / "tasks" / "phase3_tasks_v1"
EXTERNAL_DIR = ROOT / "tasks" / "external_eval_v1"

SEARCH_WEB_EXTRAS: Dict[str, Dict[str, List[Dict[str, str]]]] = {
    "search_web_001": {
        "main": [
            {"intent": "Search public news about OpenAI developer conference updates", "query": "OpenAI developer conference update public news", "topic": "OpenAI 开发者大会最新公开消息"},
            {"intent": "Search public coverage of OpenAI reasoning model benchmarks", "query": "OpenAI reasoning model benchmark coverage public web", "topic": "OpenAI 推理模型 benchmark 的公开报道"},
            {"intent": "Search public news about OpenAI API pricing changes", "query": "OpenAI API pricing change public news", "topic": "OpenAI API 定价变动的公开新闻"},
            {"intent": "Search public news about OpenAI enterprise product launches", "query": "OpenAI enterprise product launch public news", "topic": "OpenAI 企业产品发布的公开消息"},
        ],
        "external": [
            {"intent": "Search public reaction to OpenAI platform outages", "query": "OpenAI platform outage public coverage", "topic": "OpenAI 平台故障的公开报道"},
            {"intent": "Search public coverage of OpenAI safety policy updates", "query": "OpenAI safety policy update public news", "topic": "OpenAI 安全政策更新的公开消息"},
        ],
    },
    "search_web_002": {
        "main": [
            {"intent": "Search public news about Tesla price cuts", "query": "Tesla price cuts latest public news", "topic": "Tesla 最近的降价新闻"},
            {"intent": "Search public news about Tesla delivery numbers", "query": "Tesla delivery numbers latest public news", "topic": "Tesla 最近交付数据的公开消息"},
            {"intent": "Search public news about Tesla factory expansion", "query": "Tesla factory expansion public news", "topic": "Tesla 工厂扩张的公开报道"},
            {"intent": "Search public news about Tesla autopilot investigation", "query": "Tesla autopilot investigation public news", "topic": "Tesla 自动驾驶调查的公开新闻"},
        ],
        "external": [
            {"intent": "Search public news about Tesla earnings guidance", "query": "Tesla earnings guidance public coverage", "topic": "Tesla 财报指引的公开报道"},
            {"intent": "Search public news about Tesla supplier negotiations", "query": "Tesla supplier negotiations public news", "topic": "Tesla 供应链谈判的公开消息"},
        ],
    },
    "search_web_003": {
        "main": [
            {"intent": "Search public news about stroller safety recalls", "query": "stroller safety recall latest public news", "topic": "婴儿推车召回的公开新闻"},
            {"intent": "Search public news about toy battery recalls", "query": "toy battery recall latest public news", "topic": "玩具电池召回的公开新闻"},
            {"intent": "Search public news about food contamination alerts", "query": "food contamination alert public news", "topic": "食品污染警报的公开消息"},
            {"intent": "Search public news about appliance fire-risk recalls", "query": "appliance fire risk recall public news", "topic": "家电起火风险召回的公开报道"},
        ],
        "external": [
            {"intent": "Search public news about medication recall notices", "query": "medication recall public notice recent news", "topic": "药品召回公告的公开消息"},
            {"intent": "Search public news about e-bike battery recalls", "query": "e-bike battery recall latest public news", "topic": "电动自行车电池召回的公开新闻"},
        ],
    },
    "search_web_004": {
        "main": [
            {"intent": "Search a public conference registration website", "query": "KubeCon 2026 registration page public website", "topic": "KubeCon 2026 的公开注册页面"},
            {"intent": "Search a public conference CFP website", "query": "NeurIPS 2026 CFP public page", "topic": "NeurIPS 2026 的公开 CFP 页面"},
            {"intent": "Search a public summit livestream page", "query": "Google I/O livestream page public web", "topic": "Google I/O 直播页面"},
            {"intent": "Search a public conference venue page", "query": "AWS re:Invent venue map public page", "topic": "AWS re:Invent 会场地图页面"},
        ],
        "external": [
            {"intent": "Search a public workshop agenda page", "query": "ICLR workshop agenda public page", "topic": "ICLR workshop 议程页面"},
            {"intent": "Search a public meetup call-for-speakers page", "query": "AI meetup call for speakers public page", "topic": "AI meetup 征集讲者页面"},
        ],
    },
    "search_web_005": {
        "main": [
            {"intent": "Search public analyst coverage of Apple earnings", "query": "Apple earnings analyst commentary public news", "topic": "分析师对 Apple 财报的公开观点"},
            {"intent": "Search public analyst coverage of Nvidia guidance", "query": "Nvidia guidance analyst commentary public web", "topic": "分析师对 Nvidia 指引的公开评价"},
            {"intent": "Search public analyst coverage of Amazon cloud margins", "query": "Amazon cloud margins analyst commentary public news", "topic": "分析师对 Amazon 云业务利润率的公开看法"},
            {"intent": "Search public analyst coverage of Meta ad revenue", "query": "Meta ad revenue analyst commentary public news", "topic": "分析师对 Meta 广告收入的公开观点"},
        ],
        "external": [
            {"intent": "Search public analyst coverage of Google capex", "query": "Google capex analyst commentary public news", "topic": "分析师对 Google 资本开支的公开评论"},
            {"intent": "Search public analyst coverage of AMD AI roadmap", "query": "AMD AI roadmap analyst commentary public news", "topic": "分析师对 AMD AI 路线图的公开评价"},
        ],
    },
}

SEARCH_DATABASE_QUERIES: Dict[str, Dict[str, List[str]]] = {
    "customer": {"main": ["Olivia Chen", "Noah Patel", "Liam Carter", "Mia Zhang"], "external": ["Sophia Kim", "Ethan Rivera"]},
    "product": {"main": ["SKU-1002", "SKU-2048", "SKU-3301", "SKU-4410"], "external": ["SKU-5800", "SKU-6621"]},
    "employee": {"main": ["Dana Brooks", "Mason Lee", "Priya Nair", "Jordan Miles"], "external": ["Elena Gomez", "Victor Huang"]},
    "order": {"main": ["ORD-55319", "SO-77210", "CN-44820", "RET-99112"], "external": ["PO-61224", "WEB-2026-881"]},
    "ticket": {"main": ["TCK-1008", "TCK-2219", "TCK-3900", "TCK-4881"], "external": ["TCK-5902", "TCK-7001"]},
}

DOC_QUERY_POOLS: Dict[str, Dict[str, List[str]]] = {
    "hr": {"main": ["remote work stipend policy", "new-hire onboarding checklist", "promotion review timeline", "leave approval escalation path"], "external": ["manager handbook for probation review", "temporary contractor offboarding steps"]},
    "it": {"main": ["laptop disk encryption guide", "password manager setup steps", "okta enrollment instructions", "wifi certificate renewal guide"], "external": ["vpn split tunneling rules", "hardware replacement SLA"]},
    "finance": {"main": ["travel reimbursement timeline", "corporate card receipt policy", "expense audit checklist", "vendor payment approval flow"], "external": ["annual budget submission SOP", "foreign currency reimbursement rule"]},
    "operations": {"main": ["forklift inspection checklist", "warehouse shift handoff SOP", "inventory discrepancy process", "dock safety incident escalation"], "external": ["cold-chain exception handling", "returns triage checklist"]},
    "support": {"main": ["premium customer escalation matrix", "refund exception policy", "weekend paging process", "sla breach escalation steps"], "external": ["chat handoff checklist", "refund fraud review SOP"]},
}

UPDATE_ORDER_NOTES: Dict[str, Dict[str, List[str]]] = {
    "shipped": {"main": ["handoff confirmed at sorting center", "courier pickup completed", "outbound scan completed", "label scanned by carrier"], "external": ["same-day courier pickup confirmed", "cross-dock transfer to carrier complete"]},
    "cancelled": {"main": ["customer cancelled before dispatch", "payment verification failed", "inventory shortage confirmed", "duplicate order removed"], "external": ["manual fraud review requested cancellation", "merchant closed order after address mismatch"]},
    "delivered": {"main": ["customer signed for the package", "delivery photo uploaded", "locker pickup confirmed", "front desk accepted parcel"], "external": ["carrier marked final delivery complete", "recipient OTP verification passed"]},
    "packed": {"main": ["warehouse sealed carton", "items picked and packed", "packing QA completed", "fragile label applied"], "external": ["special insert added before sealing", "multi-item carton packed and weighed"]},
    "pending": {"main": ["awaiting compliance review", "waiting for payment confirmation", "QC hold requested", "address verification pending"], "external": ["manual review queue assigned", "inventory reconciliation still open"]},
}

CHANGE_FLIGHT_REASONS: Dict[str, Dict[str, List[str]]] = {
    "change_flight_001": {"main": ["client call moved", "team sync delayed", "meeting shifted again", "onsite agenda changed"], "external": ["speaker schedule moved", "hotel check-in constraint changed"]},
    "change_flight_002": {"main": ["family conflict", "visa appointment moved", "board meeting extended", "medical appointment overlap"], "external": ["school schedule conflict", "transport connection changed"]},
    "change_flight_003": {"main": ["storm warning", "airport weather delay", "heavy rain disruption", "typhoon impact"], "external": ["snow advisory", "fog disruption at departure airport"]},
    "change_flight_004": {"main": ["conference day shifted", "panel moved to next week", "venue access date changed", "sponsor rehearsal delayed"], "external": ["workshop schedule slipped", "registration day moved"]},
    "change_flight_005": {"main": ["client rescheduled meeting", "customer requested a later visit", "account review moved", "partner onboarding shifted"], "external": ["procurement review changed", "onsite demo date moved"]},
}

SUPPORT_DESCRIPTIONS: Dict[str, Dict[str, Dict[str, List[str]]]] = {
    "technical": {"main": {"priority": ["high", "high", "medium", "high"], "description": ["mobile app freezes after MFA", "dashboard spins forever on report export", "desktop client fails to sync settings", "users hit a blank screen after login"]}, "external": {"priority": ["high", "medium"], "description": ["SSO redirect loops in the browser", "webhook delivery keeps timing out"]}},
    "billing": {"main": {"priority": ["medium", "medium", "high", "medium"], "description": ["invoice still shows a cancelled add-on", "tax amount looks duplicated on renewal", "credit note never applied to the account", "annual prepayment was charged twice"]}, "external": {"priority": ["medium", "high"], "description": ["refund approved but never reached the card", "enterprise invoice has the wrong billing entity"]}},
    "order": {"main": {"priority": ["high", "medium", "high", "medium"], "description": ["tracking page stopped updating for three days", "customer received only part of the shipment", "replacement order was never released", "order shows exception after customs scan"]}, "external": {"priority": ["high", "medium"], "description": ["package was returned to sender unexpectedly", "promised gift item is missing from the carton"]}},
    "account": {"main": {"priority": ["low", "medium", "medium", "low"], "description": ["email verification link has expired", "role assignment vanished after profile edit", "account is locked after repeated MFA prompts", "self-service password reset never sends mail"]}, "external": {"priority": ["medium", "low"], "description": ["new user invitation lands on a 404 page", "deactivated account still appears in the org directory"]}},
    "travel": {"main": {"priority": ["high", "medium", "high", "medium"], "description": ["hotel booking never synced to the itinerary", "expense receipt upload failed in the trip portal", "traveler profile lost passport details", "car rental confirmation is missing from the app"]}, "external": {"priority": ["high", "medium"], "description": ["rail segment is absent from the itinerary timeline", "trip approval email points to an expired page"]}},
}

TRANSLATE_TEXT_POOLS: Dict[str, Dict[str, List[str]]] = {
    "translate_text_001": {"main": ["please join the call five minutes early", "the deployment window starts at midnight", "customer requested a revised invoice", "meeting room changed to 3B"], "external": ["maintenance starts after business hours", "please confirm receipt before noon"]},
    "translate_text_002": {"main": ["请把审批结果发给财务团队", "请在周五前完成合同签署", "请确认新的出差日期", "请把附件同步到共享盘"], "external": ["请先联系采购确认预算", "请在今天下班前回复客户"]},
    "translate_text_003": {"main": ["boarding starts at gate C12", "your passport will be checked again", "the connection time is only 40 minutes", "please proceed to the transfer desk"], "external": ["the flight is delayed due to runway traffic", "baggage claim moved to carousel seven"]},
    "translate_text_004": {"main": ["请先完成入库扫码", "今晚需要加做一轮抽检", "托盘标签已经重新打印", "拣货区临时改到 B 通道"], "external": ["冷链货物需要优先装车", "缺货商品请移到待处理区"]},
    "translate_text_005": {"main": ["请更新浏览器后再尝试", "验证码已过期，请重新获取", "系统检测到异常登录行为", "请先退出再重新进入应用"], "external": ["登录会话已失效，请重新认证", "请确认网络恢复后再次提交"]},
}


def plus_days(date_str: str, days: int) -> str:
    return (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=days)).strftime("%Y-%m-%d")


def mutate_identifier(value: str, delta: int) -> str:
    digits = []
    positions = []
    for idx, ch in enumerate(value):
        if ch.isdigit():
            digits.append(ch)
            positions.append(idx)
    if not digits:
        return f"{value}-{delta + 1}"
    number = int("".join(digits)) + delta
    padded = str(number).zfill(len(digits))
    chars = list(value)
    for idx, new_ch in zip(positions, padded):
        chars[idx] = new_ch
    return "".join(chars)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def make_task(
    base_task: TaskTemplate,
    task_id: str,
    task_set: str,
    intent: str,
    gold_params: Dict[str, Any],
    variants: Dict[str, Dict[str, Any]],
    notes: str,
) -> Dict[str, Any]:
    return {
        "task_id": task_id,
        "version": "task_v2",
        "template_family": base_task.task_id,
        "task_set": task_set,
        "intent": intent,
        "domain": base_task.domain,
        "language": base_task.language,
        "dialog_context": base_task.dialog_context,
        "gold_tool": base_task.gold_tool,
        "gold_params": gold_params,
        "distractor_tools": base_task.distractor_tools,
        "variants": variants,
        "notes": notes,
    }


def clone_base_task(base_task: TaskTemplate, task_id: str) -> Dict[str, Any]:
    task = base_task.model_dump()
    task["task_id"] = task_id
    task["version"] = "task_v2"
    task["template_family"] = base_task.task_id
    task["task_set"] = "main"
    return task


def clarification_fields(base_task: TaskTemplate) -> List[str]:
    return list(base_task.variants["incomplete"].clarification_fields)


def search_web_variants(base_task: TaskTemplate, topic: str) -> Dict[str, Dict[str, Any]]:
    if base_task.language == "zh":
        return {
            "clear": {"utterance": f"查一下公开网页上关于{topic}的最新信息。"},
            "ambiguous": {"utterance": f"帮我看看{topic}最近外面都怎么说。"},
            "incomplete": {"utterance": "帮我搜一下这个话题。", "need_clarification": True, "clarification_fields": clarification_fields(base_task)},
            "misleading": {"utterance": f"查一下{topic}的公开信息，如果内部文档或数据库里也有类似内容你也可以顺便看。"},
        }
    return {
        "clear": {"utterance": f"Search the public web for recent information about {topic}."},
        "ambiguous": {"utterance": f"Can you see what public sources are saying about {topic} lately?"},
        "incomplete": {"utterance": "Look this up for me.", "need_clarification": True, "clarification_fields": clarification_fields(base_task)},
        "misleading": {"utterance": f"Search the public web for {topic}, but if internal docs or databases mention it you can check those too."},
    }


def search_database_variants(base_task: TaskTemplate, label: str) -> Dict[str, Dict[str, Any]]:
    entity_type = base_task.gold_params["entity_type"]
    if base_task.language == "zh":
        return {
            "clear": {"utterance": f"帮我在数据库里查一下 {entity_type} 记录：{label}。"},
            "ambiguous": {"utterance": f"帮我把这个 {entity_type} 记录翻出来，关键词是 {label}。"},
            "incomplete": {"utterance": f"帮我查一下这个 {entity_type} 记录。", "need_clarification": True, "clarification_fields": clarification_fields(base_task)},
            "misleading": {"utterance": f"帮我在数据库里查 {label} 这条 {entity_type} 记录；如果公开网页或内部文档里也有类似信息你也可以看。"},
        }
    return {
        "clear": {"utterance": f"Search the database for the {entity_type} record '{label}'."},
        "ambiguous": {"utterance": f"Can you pull the {entity_type} entry for {label}?"},
        "incomplete": {"utterance": f"Look up that {entity_type} record for me.", "need_clarification": True, "clarification_fields": clarification_fields(base_task)},
        "misleading": {"utterance": f"Search the database for {label} as a {entity_type} record, and feel free to check the web or internal docs if it helps."},
    }


def docs_variants(base_task: TaskTemplate, topic: str) -> Dict[str, Dict[str, Any]]:
    if base_task.language == "zh":
        return {
            "clear": {"utterance": f"查一下内部文档里关于“{topic}”的说明。"},
            "ambiguous": {"utterance": f"帮我在内部资料里找一下 {topic}。"},
            "incomplete": {"utterance": "帮我查一下那个内部流程。", "need_clarification": True, "clarification_fields": clarification_fields(base_task)},
            "misleading": {"utterance": f"帮我查内部文档里关于 {topic} 的内容；如果公开网页或数据库里有类似材料你也可以顺手看。"},
        }
    return {
        "clear": {"utterance": f"Find the internal documentation about '{topic}'."},
        "ambiguous": {"utterance": f"Can you pull the internal doc for {topic}?"},
        "incomplete": {"utterance": "Find that internal process doc for me.", "need_clarification": True, "clarification_fields": clarification_fields(base_task)},
        "misleading": {"utterance": f"Find the internal doc for {topic}, but you can also look at public sources or database entries if they seem related."},
    }


def order_status_variants(base_task: TaskTemplate, order_id: str, external: bool = False) -> Dict[str, Dict[str, Any]]:
    if base_task.language == "zh":
        clear = f"查一下订单 {order_id} 当前的履约状态。"
        ambiguous = f"帮我看下 {order_id} 现在到哪一步了。"
        incomplete = "帮我查一下这个订单现在什么状态。"
        misleading = f"查一下订单 {order_id} 的状态；如果数据库或网页上也能找到类似信息你也可以查。"
        if external:
            ambiguous = f"{order_id} 这单客户在催，我只想知道它现在卡在哪个节点。"
    else:
        clear = f"Check the current status for order {order_id}."
        ambiguous = f"Can you tell me where {order_id} is in the fulfillment flow?"
        incomplete = "Check the status of this order for me."
        misleading = f"Check order {order_id}, and if needed you can look in the database or public web too."
        if external:
            ambiguous = f"A customer is chasing {order_id}. I only need to know its latest status."
    return {
        "clear": {"utterance": clear},
        "ambiguous": {"utterance": ambiguous},
        "incomplete": {"utterance": incomplete, "need_clarification": True, "clarification_fields": clarification_fields(base_task)},
        "misleading": {"utterance": misleading},
    }


def update_order_variants(base_task: TaskTemplate, order_id: str, status: str, note: str, external: bool = False) -> Dict[str, Dict[str, Any]]:
    if base_task.language == "zh":
        clear = f"把订单 {order_id} 更新成 {status}，并备注 {note}。"
        ambiguous = f"帮我把 {order_id} 调到 {status}，备注一下 {note}。"
        incomplete = "把这个订单状态改一下。"
        misleading = f"把订单 {order_id} 更新成 {status} 并备注 {note}；如果需要也可以顺便查一下当前状态。"
        if external:
            ambiguous = f"{order_id} 这单现在要改成 {status}，备注写 {note}。"
    else:
        clear = f"Update order {order_id} to {status} and add note {note}."
        ambiguous = f"Please move {order_id} to {status} and note {note}."
        incomplete = "Update this order status for me."
        misleading = f"Update order {order_id} to {status} with note {note}; you can also inspect its status if needed."
        if external:
            ambiguous = f"For order {order_id}, set the status to {status} and note {note}."
    return {
        "clear": {"utterance": clear},
        "ambiguous": {"utterance": ambiguous},
        "incomplete": {"utterance": incomplete, "need_clarification": True, "clarification_fields": clarification_fields(base_task)},
        "misleading": {"utterance": misleading},
    }


def book_flight_variants(base_task: TaskTemplate, params: Dict[str, Any], external: bool = False) -> Dict[str, Dict[str, Any]]:
    if base_task.language == "zh":
        clear = f"帮我预订 {params['date']} 的 {params['flight_no']}，从 {params['origin']} 到 {params['destination']}，{params['seat_class']}。"
        ambiguous = f"把 {params['date']} 那班 {params['flight_no']} 订了吧，{params['origin']} 飞 {params['destination']}，{params['seat_class']}。"
        incomplete = f"帮我订 {params['flight_no']} 的航班。"
        misleading = f"帮我预订 {params['date']} 的 {params['flight_no']}，从 {params['origin']} 到 {params['destination']}，{params['seat_class']}；如果需要你也可以先去网页查公开信息。"
        if external:
            ambiguous = f"{params['date']} 我得从 {params['origin']} 去 {params['destination']}，就订 {params['flight_no']}，{params['seat_class']}。"
    else:
        clear = f"Book flight {params['flight_no']} on {params['date']} from {params['origin']} to {params['destination']} in {params['seat_class']}."
        ambiguous = f"Please lock in {params['flight_no']} for {params['date']} from {params['origin']} to {params['destination']} in {params['seat_class']}."
        incomplete = f"Book {params['flight_no']} for me."
        misleading = f"Book flight {params['flight_no']} on {params['date']} from {params['origin']} to {params['destination']} in {params['seat_class']}; you can search the web if needed."
        if external:
            ambiguous = f"I need {params['flight_no']} on {params['date']} from {params['origin']} to {params['destination']}, {params['seat_class']} seat if possible."
    return {
        "clear": {"utterance": clear},
        "ambiguous": {"utterance": ambiguous},
        "incomplete": {"utterance": incomplete, "need_clarification": True, "clarification_fields": clarification_fields(base_task)},
        "misleading": {"utterance": misleading},
    }


def change_flight_variants(base_task: TaskTemplate, params: Dict[str, Any], external: bool = False) -> Dict[str, Dict[str, Any]]:
    if base_task.language == "zh":
        clear = f"把预订 {params['booking_id']} 改到 {params['new_date']}，原因是 {params['reason']}。"
        ambiguous = f"帮我把 {params['booking_id']} 改到 {params['new_date']}，因为 {params['reason']}。"
        incomplete = "帮我把机票改签一下。"
        misleading = f"把预订 {params['booking_id']} 改到 {params['new_date']}，原因是 {params['reason']}；如果你想先查公开航班信息也可以。"
        if external:
            ambiguous = f"{params['booking_id']} 这张票得改到 {params['new_date']}，原因是 {params['reason']}。"
    else:
        clear = f"Change booking {params['booking_id']} to {params['new_date']} because {params['reason']}."
        ambiguous = f"Please move {params['booking_id']} to {params['new_date']} due to {params['reason']}."
        incomplete = "Please change my flight booking."
        misleading = f"Change booking {params['booking_id']} to {params['new_date']} because {params['reason']}. You can also search the public web if it helps."
        if external:
            ambiguous = f"I need {params['booking_id']} moved to {params['new_date']} since {params['reason']}."
    return {
        "clear": {"utterance": clear},
        "ambiguous": {"utterance": ambiguous},
        "incomplete": {"utterance": incomplete, "need_clarification": True, "clarification_fields": clarification_fields(base_task)},
        "misleading": {"utterance": misleading},
    }


def support_ticket_variants(base_task: TaskTemplate, params: Dict[str, Any], external: bool = False) -> Dict[str, Dict[str, Any]]:
    if base_task.language == "zh":
        clear = f"为用户 {params['user_id']} 创建一个 {params['priority']} 优先级的 {params['category']} 工单，问题是 {params['description']}。"
        ambiguous = f"帮我给 {params['user_id']} 开个 {params['category']} 工单，优先级 {params['priority']}，问题是 {params['description']}。"
        incomplete = "帮我开一个这个用户的支持工单。"
        misleading = f"为用户 {params['user_id']} 创建一个 {params['priority']} 优先级的 {params['category']} 工单，问题是 {params['description']}；如果内部文档或订单系统能提供背景你也可以看。"
        if external:
            ambiguous = f"{params['user_id']} 需要一个 {params['category']} 工单，优先级 {params['priority']}，问题是 {params['description']}。"
    else:
        clear = f"Create a {params['priority']}-priority {params['category']} ticket for user {params['user_id']} because {params['description']}."
        ambiguous = f"Open a {params['priority']} {params['category']} ticket for {params['user_id']}. The issue is {params['description']}."
        incomplete = "Open a support ticket for this user."
        misleading = f"Create a {params['priority']}-priority {params['category']} ticket for user {params['user_id']} because {params['description']}. You can also inspect related docs or order data if useful."
        if external:
            ambiguous = f"Please create a {params['category']} case for {params['user_id']} with {params['priority']} priority. The problem is {params['description']}."
    return {
        "clear": {"utterance": clear},
        "ambiguous": {"utterance": ambiguous},
        "incomplete": {"utterance": incomplete, "need_clarification": True, "clarification_fields": clarification_fields(base_task)},
        "misleading": {"utterance": misleading},
    }


def weather_variants(base_task: TaskTemplate, city: str, date: str, external: bool = False) -> Dict[str, Dict[str, Any]]:
    if base_task.language == "zh":
        clear = f"查一下 {date} {city} 的天气。"
        ambiguous = f"帮我看下 {city} 在 {date} 的天气怎么样。"
        incomplete = "帮我查一下那天的天气。"
        misleading = f"查一下 {date} {city} 的天气，如果公开网页上有相关内容你也可以顺便搜。"
        if external:
            ambiguous = f"我那天要去 {city}，想知道 {date} 天气大概怎么样。"
    else:
        clear = f"Get the weather for {city} on {date}."
        ambiguous = f"What will the weather be like in {city} on {date}?"
        incomplete = "Can you check the weather for me?"
        misleading = f"Get the weather for {city} on {date}. If web search helps, you can do that too."
        if external:
            ambiguous = f"I'll be in {city} on {date}. What should I expect weather-wise?"
    return {
        "clear": {"utterance": clear},
        "ambiguous": {"utterance": ambiguous},
        "incomplete": {"utterance": incomplete, "need_clarification": True, "clarification_fields": clarification_fields(base_task)},
        "misleading": {"utterance": misleading},
    }


def translate_variants(base_task: TaskTemplate, text: str, target_lang: str, external: bool = False) -> Dict[str, Dict[str, Any]]:
    if base_task.language == "zh":
        clear = f"把“{text}”翻译成 {target_lang}。"
        ambiguous = f"帮我把“{text}”翻成 {target_lang}。"
        incomplete = "帮我翻译一下这句话。"
        misleading = f"把“{text}”翻译成 {target_lang}，如果网页或内部文档里有类似表达你也可以参考。"
        if external:
            ambiguous = f"我需要把“{text}”处理成 {target_lang}。"
    else:
        clear = f"Translate '{text}' to {target_lang}."
        ambiguous = f"Can you put '{text}' into {target_lang} for me?"
        incomplete = "Translate this sentence for me."
        misleading = f"Translate '{text}' to {target_lang}. If related docs or web examples help, you can check them too."
        if external:
            ambiguous = f"How should I say '{text}' in {target_lang}?"
    return {
        "clear": {"utterance": clear},
        "ambiguous": {"utterance": ambiguous},
        "incomplete": {"utterance": incomplete, "need_clarification": True, "clarification_fields": clarification_fields(base_task)},
        "misleading": {"utterance": misleading},
    }


def search_database_record(base_task: TaskTemplate, label: str) -> Dict[str, Any]:
    params = dict(base_task.gold_params)
    params["query"] = label
    params["limit"] = 5
    entity_type = params["entity_type"]
    intent = f"查询数据库中的 {entity_type} 记录：{label}" if base_task.language == "zh" else f"Lookup a {entity_type} record for {label}"
    return {"intent": intent, "gold_params": params, "variants": search_database_variants(base_task, label), "notes": f"Phase 3 expanded {entity_type} database lookup."}


def query_internal_docs_record(base_task: TaskTemplate, topic: str) -> Dict[str, Any]:
    params = dict(base_task.gold_params)
    params["query"] = topic
    intent = f"查找内部文档：{topic}" if base_task.language == "zh" else f"Find the internal doc for {topic}"
    return {"intent": intent, "gold_params": params, "variants": docs_variants(base_task, topic), "notes": "Phase 3 expanded internal-doc retrieval request."}


def query_order_status_record(base_task: TaskTemplate, delta: int, external: bool = False) -> Dict[str, Any]:
    order_id = mutate_identifier(base_task.gold_params["order_id"], delta)
    params = {"order_id": order_id}
    intent = f"{base_task.intent} for {order_id}" if base_task.language == "en" else f"{base_task.intent}：{order_id}"
    return {"intent": intent, "gold_params": params, "variants": order_status_variants(base_task, order_id, external=external), "notes": "Phase 3 expanded order-status query."}


def update_order_record(base_task: TaskTemplate, delta: int, note: str, external: bool = False) -> Dict[str, Any]:
    order_id = mutate_identifier(base_task.gold_params["order_id"], delta)
    params = {"order_id": order_id, "status": base_task.gold_params["status"], "note": note}
    intent = f"{base_task.intent} for {order_id}" if base_task.language == "en" else f"{base_task.intent}：{order_id}"
    return {"intent": intent, "gold_params": params, "variants": update_order_variants(base_task, order_id, params["status"], note, external=external), "notes": "Phase 3 expanded order mutation sample."}


def book_flight_record(base_task: TaskTemplate, delta: int, external: bool = False) -> Dict[str, Any]:
    params = dict(base_task.gold_params)
    params["date"] = plus_days(params["date"], delta)
    params["flight_no"] = mutate_identifier(params["flight_no"], delta)
    seat_classes = ["economy", "premium_economy", "business", "economy", "business", "premium_economy"]
    params["seat_class"] = seat_classes[delta % len(seat_classes)]
    intent = f"{base_task.intent} on {params['date']}" if base_task.language == "en" else f"{base_task.intent}（{params['date']}）"
    return {"intent": intent, "gold_params": params, "variants": book_flight_variants(base_task, params, external=external), "notes": "Phase 3 expanded booking sample."}


def change_flight_record(base_task: TaskTemplate, delta: int, reason: str, external: bool = False) -> Dict[str, Any]:
    params = dict(base_task.gold_params)
    params["booking_id"] = mutate_identifier(params["booking_id"], delta)
    params["new_date"] = plus_days(params["new_date"], delta)
    params["reason"] = reason
    intent = f"{base_task.intent} for {params['booking_id']}" if base_task.language == "en" else f"{base_task.intent}：{params['booking_id']}"
    return {"intent": intent, "gold_params": params, "variants": change_flight_variants(base_task, params, external=external), "notes": "Phase 3 expanded rebooking sample."}


def create_support_ticket_record(base_task: TaskTemplate, delta: int, priority: str, description: str, external: bool = False) -> Dict[str, Any]:
    params = dict(base_task.gold_params)
    params["user_id"] = mutate_identifier(params["user_id"], delta)
    params["priority"] = priority
    params["description"] = description
    intent = f"{base_task.intent} for {params['user_id']}" if base_task.language == "en" else f"{base_task.intent}：{params['user_id']}"
    return {"intent": intent, "gold_params": params, "variants": support_ticket_variants(base_task, params, external=external), "notes": "Phase 3 expanded support-ticket sample."}


def get_weather_record(base_task: TaskTemplate, delta: int, external: bool = False) -> Dict[str, Any]:
    params = dict(base_task.gold_params)
    params["date"] = plus_days(params["date"], delta)
    intent = f"{base_task.intent} on {params['date']}" if base_task.language == "en" else f"{base_task.intent}（{params['date']}）"
    return {"intent": intent, "gold_params": params, "variants": weather_variants(base_task, params["city"], params["date"], external=external), "notes": "Phase 3 expanded weather sample."}


def translate_text_record(base_task: TaskTemplate, text: str, external: bool = False) -> Dict[str, Any]:
    params = dict(base_task.gold_params)
    params["text"] = text
    intent = f"{base_task.intent}: {text}" if base_task.language == "en" else f"{base_task.intent}：{text}"
    return {"intent": intent, "gold_params": params, "variants": translate_variants(base_task, text, params["target_lang"], external=external), "notes": "Phase 3 expanded translation sample."}


def search_web_record(base_task: TaskTemplate, payload: Dict[str, str]) -> Dict[str, Any]:
    params = dict(base_task.gold_params)
    params["query"] = payload["query"]
    params["max_results"] = 5
    return {"intent": payload["intent"], "gold_params": params, "variants": search_web_variants(base_task, payload["topic"]), "notes": "Phase 3 expanded public-web search request."}


def build_extra_records(base_task: TaskTemplate, task_set: str) -> List[Dict[str, Any]]:
    external = task_set == "external_eval"
    if base_task.gold_tool == "search_web":
        payloads = SEARCH_WEB_EXTRAS[base_task.task_id]["external" if external else "main"]
        return [search_web_record(base_task, payload) for payload in payloads]
    if base_task.gold_tool == "search_database":
        entity_type = base_task.gold_params["entity_type"]
        labels = SEARCH_DATABASE_QUERIES[entity_type]["external" if external else "main"]
        return [search_database_record(base_task, label) for label in labels]
    if base_task.gold_tool == "query_internal_docs":
        department = base_task.gold_params.get("department")
        topics = DOC_QUERY_POOLS[department]["external" if external else "main"]
        return [query_internal_docs_record(base_task, topic) for topic in topics]
    if base_task.gold_tool == "query_order_status":
        deltas = [11, 22] if external else [3, 7, 12, 18]
        return [query_order_status_record(base_task, delta, external=external) for delta in deltas]
    if base_task.gold_tool == "update_order":
        notes = UPDATE_ORDER_NOTES[base_task.gold_params["status"]]["external" if external else "main"]
        deltas = [15, 27] if external else [4, 9, 16, 23]
        return [update_order_record(base_task, delta, note, external=external) for delta, note in zip(deltas, notes)]
    if base_task.gold_tool == "book_flight":
        deltas = [45, 61] if external else [5, 12, 19, 33]
        return [book_flight_record(base_task, delta, external=external) for delta in deltas]
    if base_task.gold_tool == "change_flight":
        reasons = CHANGE_FLIGHT_REASONS[base_task.task_id]["external" if external else "main"]
        deltas = [25, 40] if external else [3, 8, 15, 22]
        return [change_flight_record(base_task, delta, reason, external=external) for delta, reason in zip(deltas, reasons)]
    if base_task.gold_tool == "create_support_ticket":
        family = SUPPORT_DESCRIPTIONS[base_task.gold_params["category"]]["external" if external else "main"]
        deltas = [30, 44] if external else [5, 11, 19, 27]
        return [
            create_support_ticket_record(base_task, delta, priority, description, external=external)
            for delta, priority, description in zip(deltas, family["priority"], family["description"])
        ]
    if base_task.gold_tool == "get_weather":
        deltas = [65, 92] if external else [3, 10, 17, 24]
        return [get_weather_record(base_task, delta, external=external) for delta in deltas]
    if base_task.gold_tool == "translate_text":
        texts = TRANSLATE_TEXT_POOLS[base_task.task_id]["external" if external else "main"]
        return [translate_text_record(base_task, text, external=external) for text in texts]
    raise ValueError(f"Unsupported tool: {base_task.gold_tool}")


def generate_assets() -> None:
    base_tasks = load_tasks(str(ROOT / "tasks" / "base_tasks_v1" / "*.json"))
    grouped: Dict[str, List[TaskTemplate]] = {}
    for task in base_tasks:
        grouped.setdefault(task.gold_tool, []).append(task)

    if MAIN_DIR.exists():
        shutil.rmtree(MAIN_DIR)
    if EXTERNAL_DIR.exists():
        shutil.rmtree(EXTERNAL_DIR)
    MAIN_DIR.mkdir(parents=True, exist_ok=True)
    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)

    for tool_name, tool_tasks in grouped.items():
        tool_tasks = sorted(tool_tasks, key=lambda item: item.task_id)
        main_rows: List[Dict[str, Any]] = []
        external_rows: List[Dict[str, Any]] = []
        main_index = 1
        external_index = 1

        for base_task in tool_tasks:
            main_rows.append(clone_base_task(base_task, f"{tool_name}_{main_index:03d}"))
            main_index += 1

            for record in build_extra_records(base_task, "main"):
                main_rows.append(make_task(base_task, f"{tool_name}_{main_index:03d}", "main", record["intent"], record["gold_params"], record["variants"], record["notes"]))
                main_index += 1

            for record in build_extra_records(base_task, "external_eval"):
                external_rows.append(make_task(base_task, f"{tool_name}_ext_{external_index:03d}", "external_eval", record["intent"], record["gold_params"], record["variants"], record["notes"]))
                external_index += 1

        write_json(MAIN_DIR / f"{tool_name}.json", main_rows)
        write_json(EXTERNAL_DIR / f"{tool_name}.json", external_rows)


def main() -> None:
    generate_assets()
    print(f"Generated main task pool at {MAIN_DIR}")
    print(f"Generated external eval task pool at {EXTERNAL_DIR}")


if __name__ == "__main__":
    main()
