# Phase 3 标注规范

本规范用于人工复核 `tool calling` 结果，并对自动评估器的边界情况做仲裁。

## 1. 标注对象

每条待复核样本至少包含：

- `sample_id`
- `task_id`
- `variant_name`
- `messages`
- `gold_tool`
- `gold_params`
- `prediction.tool_name_pred`
- `prediction.arguments_pred`
- 自动评估结果

## 2. 一级主标签

### `correct`

满足以下条件时标为 `correct`：

- 工具选择正确
- 参数键完整且无多余关键参数
- grounded 参数值与 gold 一致
- 对于本应调用工具的样本，没有错误地转成澄清或空响应
- 对于应澄清的样本，没有调用工具，且追问了实际缺失的关键字段

### `wrong_tool`

满足以下任一条件时标为 `wrong_tool`：

- 选择了错误工具
- 本应调用工具，但没有调用任何工具
- 用了高风险但不匹配的工具

### `param_error`

工具正确，但参数层面存在问题时标为 `param_error`。常见子类：

- `missing_required_param`
- `extra_param`
- `param_type_error`
- `param_value_hallucination`
- `param_value_mismatch`

### `should_clarify_but_called`

对于 `incomplete` 或其他缺失关键槽位的请求，如果模型直接调用工具而没有先澄清，则标为 `should_clarify_but_called`。

### `clarification_error`

任务需要澄清且模型没有调用工具时，空回复记为 `empty_clarification_reply`。有正文但没有追问全部缺失项时，记为 `missing_clarification_fields`。自动评分根据请求语句、问句和列表中的双语字段线索判定，间接表达由人工仲裁。

## 3. 二级子标签判定

### `missing_required_param`

- schema 中 required 的参数未出现
- 或参数存在但为空、不可解析且不能视为有效值

### `extra_param`

- 参数键不在工具 schema 中
- 自动补出未定义字段也算

### `param_type_error`

- 类型与 schema 不符
- 如字符串字段被填成布尔值，整数字段被填成对象

### `param_value_hallucination`

- 参数键正确，类型也正确
- 但 grounded 参数值与用户输入事实不一致
- 例如订单号、状态、日期、城市、booking_id 被“脑补”
- 对工具接受自由文本的城市名和目标语言，项目词表中的中英文等价写法均可接受。结构化 ID、枚举和开放文本仍按现有比对规范处理。
- 请求给出月日但缺少年份，且没有对话日期可作依据时，应澄清年份。直接填完整日期记为 `should_clarify_but_called`，同时加 `unsupported_date_year` 和 `param_value_hallucination` 子标签，即使填入年份恰好等于 gold。

### `param_value_mismatch`

- 非 grounded 参数存在偏差
- 可以记为错误，但强度低于 hallucination

### `high_risk_tool_misuse`

- 误用了 `risk_level=high` 的工具
- 如 `update_order`

## 4. 澄清判定规则

以下情况默认应先澄清：

- 缺失 required 槽位
- 用户说的是“这个”“那个”“上一单”“那张票”但没有实体标识
- 日期、城市、订单号、booking_id 等关键 grounding 信息缺失

以下情况默认不用澄清：

- 用户已经明确提供了所需槽位
- 仅有措辞模糊，但 gold 目标仍唯一清晰

任务生成器的原始字段保留在 `task_metadata.csv`。本轮用于评分的字段见 `eval_clarification_fields`，其中包括受影响的生成模板和日期情形的修正。没有确认的缺失项和词汇匹配边界可通过人工仲裁修订。

## 5. 人工复核优先级

优先人工检查以下样本：

- 自动评估器给出 `should_clarify_but_called`
- 自动评估器给出 `param_value_hallucination`
- 高风险工具 `update_order`
- `misleading` 变体
- external_eval 样本

## 6. 争议处理

出现争议时：

1. 先记录原始用户请求和工具输出
2. 记录自动评估器给出的主标签与子标签
3. 记录人工判定
4. 在 `adjudication.csv` 中写明最终裁定和理由

## 7. 最小人工复核建议

Phase 3 建议至少做：

- 随机抽样 `100~150` 条
- 覆盖 `train / dev / test / external_eval`
- 覆盖 `zh / en`
- 覆盖 10 个工具
- 覆盖四类 variant

如果只有一个标注者，建议隔几天后对其中 `30~50` 条做延时复标。
