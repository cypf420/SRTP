# 期中自动标签抽查

复核范围为主任务 train/dev。参数部分逐条核对其中所有 18 条 `param_value_hallucination`。澄清部分在「按任务定义应该澄清、模型没有调用」的记录中，每个模型按 `(run_id, sample_id)` 排序后用同一个 `random.Random(42)` 依模型名排序各抽 10 条。复核对照了请求、工具参数规范、基准值和实际回复。

这是 Codex 对现有记录的阅读复核。下列观察保留原始自动标签，供成员复查和填写人工仲裁表。

## 参数幻构标签

| 观察 | GLM | Qwen | 实例 |
| --- | ---: | ---: | --- |
| 请求没有给年份，模型自行补了年份，任务指定的 gold 年份同样缺少文本依据 | 2 | 7 | 天气请求 `get_weather_001__ambiguous` 只说「5 月 11 号」。gold 为 2026，GLM 填 2025，Qwen 填 2023。年份字段的判定需和澄清目标一起修订。 |
| 语言名称语义相同，字符串形式不同 | 1 | 4 | GLM 的「西班牙语」对应 `Spanish`，Qwen 的「中文」对应 `Chinese`。`target_lang` 为自由字符串，工具规范未限定英语语言名。 |
| 请求明确指定的工单类别或优先级被模型改写 | 0 | 4 | `create_support_ticket_013__ambiguous` 明确要求 `medium`，Qwen 填 `high`。 |

每条记录按上表的主要问题归类。部分记录还包含其他字段差异，例如 Qwen 在 `book_flight_021__ambiguous` 同时自行补了年份，并把「高经舱」填成「商务」。参数错误大类也含自由文本改写等差异，本次仅复核 `param_value_hallucination` 子标签。

| 模型 | 主要问题 | 已复核的 `sample_id` |
| --- | --- | --- |
| GLM | 自行补年份 | `book_flight_011__ambiguous`、`get_weather_001__ambiguous` |
| GLM | 同义值 | `translate_text_021__ambiguous` |
| Qwen | 自行补年份 | `book_flight_001__ambiguous`、`book_flight_006__ambiguous`、`book_flight_011__ambiguous`、`book_flight_021__ambiguous`、`change_flight_006__ambiguous`、`change_flight_016__ambiguous`、`get_weather_001__ambiguous` |
| Qwen | 同义值 | `translate_text_002__ambiguous`、`translate_text_003__ambiguous`、`translate_text_004__ambiguous`、`translate_text_005__ambiguous` |
| Qwen | 显式值被改写 | `create_support_ticket_012__ambiguous`、`create_support_ticket_013__ambiguous`、`create_support_ticket_015__ambiguous`、`create_support_ticket_023__clear` |

## 澄清回复

20 条回复都有正文。16 条覆盖所有已标缺失项，且复核未发现影响任务执行的追问遗漏。以下四条需要修正评估规则或复查任务标注。

| 模型 | `sample_id` | 请求与实际回复 | 复核意见 |
| --- | --- | --- | --- |
| Qwen | `create_support_ticket_022__incomplete` | 请求给「这个用户」开工单。回复问类别、优先级和问题描述。 | 追问漏了用户标识。 |
| Qwen | `translate_text_002__incomplete` | 请求翻译「这句话」，正文和目标语言都缺失。回复只问要翻成哪种语言。 | 追问漏了待翻译原文。 |
| Qwen | `translate_text_015__incomplete` | 同样缺正文和目标语言。回复只问目标语言。 | 自动标注也只列了 `target_lang`。应复核任务缺失项。 |
| Qwen | `search_database_003__incomplete` | 请求查找「那位客户」的记录。回复问客户 ID 或识别信息。 | 回复追问了缺失的识别信息。「客户」已给出实体类型，当前 gold 同时要求澄清 `entity_type`。应复核任务缺失项。 |

其余 16 条的追溯索引如下。

- GLM 的 `book_flight_007__incomplete`、`change_flight_007__incomplete`、`change_flight_009__incomplete`、`change_flight_016__incomplete`、`create_support_ticket_018__incomplete`、`create_support_ticket_023__incomplete`、`get_weather_006__incomplete`、`translate_text_016__incomplete`、`update_order_016__incomplete`、`update_order_017__incomplete`。
- Qwen 的 `book_flight_009__incomplete`、`book_flight_010__incomplete`、`change_flight_005__incomplete`、`change_flight_006__incomplete`、`create_support_ticket_018__incomplete`、`update_order_012__incomplete`。
