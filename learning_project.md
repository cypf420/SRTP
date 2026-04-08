# SRTP 项目学习计划

## 1. 先回答：完整学会这个项目需要多久？

结合你现在的基础：

- 你已经学完 `C / C++`，说明编程逻辑、函数、模块、调试、数据结构理解不会太差。
- 你从 3 月开始学 `Python` 和数据库，说明你已经进入“能看代码”的阶段，但离“能独立维护一个 Python 研究仓库”还有一段距离。
- 这个项目不是纯 Python 练习，它还包含：
  - `tool calling`
  - `prompt / schema / task` 设计
  - `pydantic / yaml / json`
  - `实验跑数`
  - `评估器`
  - `embedding / hidden states`
  - `因果分析`

所以“完整学会”不能只理解代码，还要能自己继续推进后面的 Phase 3~5。

我给你的现实判断是：

- 达到“能跑通仓库、知道每个目录是干什么的”：`2~3 周`
- 达到“能独立修改 task / tool / prompt / evaluator”：`5~6 周`
- 达到“能独立推进这个项目后续研究工作”：`10~12 周`

推荐方案：

- 周期：`12 周`
- 强度：`每天 2.5~3.5 小时`
- 节奏：`每周 6 天学习 + 1 天复盘`

如果你每天只有 `1 小时`，大概率要拉长到 `16 周左右`。  
如果你每天能稳定投入 `4 小时以上`，可以压到 `8~9 周`，但前提是执行力非常稳定。

## 2. 这里的“学会”具体指什么？

完成这份计划后，你应该具备下面四个能力：

### Level 1：能跑

- 能配置 `conda`
- 能运行仓库里的检查脚本
- 能看懂 README 和工程计划

### Level 2：能读

- 能看懂 `runner / evaluator / scripts / tasks / tools`
- 能知道一条样本是怎么从任务模板走到评估结果的

### Level 3：能改

- 能自己新增一个 tool schema
- 能自己写 task 变体
- 能自己改 evaluator 规则并补测试

### Level 4：能继续做研究

- 能理解 Phase 3~5 为什么这么设计
- 能自己整理数据、提特征、做基础分析
- 能看懂边界分析和因果分析在这个项目里的位置

## 3. 学习原则

你现在不要按“先把 Python 学到很熟再碰项目”的方式来做。  
更高效的方式是：`边学 Python，边读这个仓库`。

学习顺序建议固定为：

1. 先把环境和仓库跑通
2. 再读项目主链路
3. 再补 Python 工程写法
4. 再补 LLM / tool calling
5. 最后补表示分析和因果分析

你现在不用把数据库当主线。  
数据库知识在这个项目里有帮助，但当前优先级明显低于：

- Python
- JSON / YAML
- 命令行
- Git / GitHub
- LLM tool calling
- pandas
- 基础统计

## 3.1 当前仓库已经多了哪些 Phase 3 文件

你现在学习时，不能只盯着 Phase 2 文件了。当前仓库已经有了这些 Phase 3 资产：

- `tasks/phase3_tasks_v1/`
- `tasks/external_eval_v1/`
- `data/annotations/annotation_guideline.md`
- `data/processed/split.csv`
- `data/processed/task_metadata.csv`
- `data/processed/data_card.md`
- `scripts/generate_phase3_assets.py`
- `scripts/build_phase3_processed.py`
- `scripts/validate_phase3_assets.py`
- `configs/runs/phase3_*.yaml`

这意味着你在“学会这个项目”时，除了 runner 和 evaluator，还要额外学会三件事：

1. 任务池是怎么从 `50` 条 seed task 扩成正式 Phase 3 资产的
2. `split.csv` 和 `task_metadata.csv` 是怎么生成的
3. 为什么现在 processed 目录里有些文件已经有内容，有些还是空的

## 4. 建议的每日学习模板

每天建议固定成这个结构：

- `40~60 分钟`：读代码 / 读文档
- `60~90 分钟`：自己跑命令 / 改小代码 / 写小实验
- `20~30 分钟`：做学习笔记
- `10~15 分钟`：回答“今天新增理解了什么”

每天都要留下至少一个产出：

- 一份笔记
- 一张流程图
- 一个命令记录
- 一个小测试
- 一个很小的代码修改

---

## 5. 12 周逐日学习安排

## 第 1 周：先把环境和 Python 工程基础补到能读仓库

### Day 1
- 学什么：项目目标、目录结构、当前完成到哪一步
- 看什么：`README_CN.md`、`engineering_plan_cn.md`
- 动手做：激活 `srtp` 环境，运行 `python scripts/check_env.py`
- 产出：写一页“这个项目在研究什么，不在研究什么”

### Day 2
- 学什么：Python 基础语法复习，重点是 `list / dict / function / import`
- 看什么：`scripts/check_env.py`
- 动手做：把脚本里你不熟的 Python 语法全部记下来并查清
- 产出：一份“我目前 Python 不熟的点”清单

### Day 3
- 学什么：Python 工程里最重要的三件事：`Path`、`json`、`yaml`
- 看什么：`runner/io_utils.py`
- 动手做：自己写一个 20 行以内的小脚本，练习读 JSON 和 YAML
- 产出：一份你自己写的小脚本

### Day 4
- 学什么：`pydantic`、类型标注、数据模型
- 看什么：`runner/schemas.py`
- 动手做：逐个说清 `ToolSchema`、`TaskTemplate`、`RunConfig` 是干什么的
- 产出：一张“schema 关系图”

### Day 5
- 学什么：命令行参数、`argparse`、脚本入口
- 看什么：`scripts/validate_assets.py`、`scripts/smoke_test_tool_call.py`
- 动手做：运行 `python scripts/validate_assets.py`
- 产出：解释这两个脚本分别解决什么问题

### Day 6
- 学什么：测试是什么，为什么这个仓库需要 `pytest`
- 看什么：`tests/test_evaluator.py`
- 动手做：运行 `python -m pytest tests/test_evaluator.py`
- 产出：写出 3 个测试分别在验证什么

### Day 7
- 学什么：本周复盘
- 动手做：不看文档，口头讲 5 分钟“这个仓库的最小主链路”
- 产出：一份第 1 周总结

## 第 2 周：把静态资产读懂

### Day 8
- 学什么：Phase 0~6 在干什么
- 看什么：`engineering_plan_cn.md`
- 动手做：把每个 Phase 用一句话总结
- 产出：你的 Phase 总表

### Day 9
- 学什么：工具 schema 是什么，为什么这个项目先定义工具
- 看什么：`tools/tool_schemas_v1.json`
- 动手做：把 10 个工具分成 3 类并说明研究作用
- 产出：一份“10 个工具的用途说明”

### Day 10
- 学什么：任务模板结构
- 看什么：`tasks/base_tasks_v1/*.json`
- 动手做：任选 5 个 task，拆出 `gold_tool / gold_params / variants`
- 产出：5 条 task 的人工解析笔记

### Day 11
- 学什么：`clear / ambiguous / incomplete / misleading` 四类变体的差别
- 看什么：继续看 `tasks/base_tasks_v1/*.json`
- 动手做：自己给任意 2 个 task 重写一版变体
- 产出：2 组你自己写的变体

### Day 12
- 学什么：系统 prompt 在这个项目里的作用
- 看什么：`prompts/system_prompt_v1.txt`
- 动手做：用自己的话重写 prompt 的行为约束
- 产出：一页“prompt 在限制模型什么”

### Day 13
- 学什么：配置文件设计
- 看什么：`configs/models/*.yaml`、`configs/runs/sample_run_v1.yaml`、`configs/runs/phase3_*.yaml`
- 动手做：逐字段解释模型配置和运行配置
- 产出：一张配置字段说明表

### Day 14
- 学什么：本周复盘
- 动手做：画出 `task -> prompt -> model -> prediction -> evaluation` 流程图
- 产出：一张完整链路图

## 第 3 周：把 runner 主链路读懂

### Day 15
- 学什么：消息是如何构造的
- 看什么：`runner/prompting.py`
- 动手做：手写一个 `messages` 列表，模拟一条样本输入
- 产出：一条你自己构造的 messages 示例

### Day 16
- 学什么：OpenAI tool schema 是怎么从内部 schema 转出去的
- 看什么：`runner/prompting.py`
- 动手做：把一个 `ToolSchema` 手工转换成 OpenAI tools 格式
- 产出：一份转换示例

### Day 17
- 学什么：模型客户端如何工作
- 看什么：`runner/client.py`
- 动手做：说清 `api_key_env`、`base_url_env`、`tool_choice`、`parse_error` 的作用
- 产出：一份 `client.py` 逐段解释

### Day 18
- 学什么：I/O 工具函数的职责拆分
- 看什么：`runner/io_utils.py`
- 动手做：说明为什么 `load_tools`、`load_tasks`、`write_jsonl` 要独立存在
- 产出：一页模块职责说明

### Day 19
- 学什么：实验元数据和可复现性
- 看什么：`runner/metadata.py`
- 动手做：理解 `run_id`、时间戳、git 元信息为什么重要
- 产出：一页“为什么实验必须记录元数据”

### Day 20
- 学什么：批量运行主入口
- 看什么：`runner/run_batch.py`
- 动手做：运行 `python runner/run_batch.py --help`
- 产出：用自己的话讲清 `main()` 做了哪几步

### Day 21
- 学什么：本周复盘
- 动手做：不看代码，写出 `run_batch.py` 的调用顺序
- 产出：一张函数调用链

## 第 4 周：把 evaluator 和测试逻辑吃透

### Day 22
- 学什么：错误标签体系
- 看什么：`evaluator/rules.py`
- 动手做：把 `correct / wrong_tool / param_error / should_clarify_but_called` 四类主标签讲清
- 产出：一张标签说明表

### Day 23
- 学什么：什么叫 grounded value hallucination
- 看什么：`evaluator/rules.py`、`tests/test_evaluator.py`
- 动手做：解释为什么 `status=cancelled` 会被标成 hallucination
- 产出：一页“grounded 参数为什么关键”

### Day 24
- 学什么：评估脚本如何把 `episodes.jsonl` 变成 CSV
- 看什么：`evaluator/evaluate_runs.py`
- 动手做：说清为什么这里要用 `pandas`
- 产出：一页 `evaluate_runs.py` 解析

### Day 25
- 学什么：人工评估和规则评估的关系
- 动手做：从任务里手工挑 10 条样本，自己先判标签，再和规则逻辑对照
- 产出：一份你自己的人工标注记录

### Day 26
- 学什么：如何为规则补测试
- 看什么：`tests/test_evaluator.py`
- 动手做：自己加 1 个测试用例，验证 `wrong_tool` 或 `missing_required_param`
- 产出：一个你自己写的测试

### Day 27
- 学什么：为什么这个项目不能只看模型输出，还必须有 evaluator
- 动手做：写一段 300 字说明
- 产出：一段“评估器的研究价值”总结

### Day 28
- 学什么：本周复盘
- 动手做：把 `task`、`prediction`、`evaluation result` 三者关系讲清
- 产出：一张从样本到标签的流程图

## 第 5 周：补齐 tool calling 和 API 调用理解

### Day 29
- 学什么：什么是 `tool calling / function calling`
- 动手做：结合本项目举 3 个例子说明“为什么不能只让模型自由回答”
- 产出：一页概念笔记

### Day 30
- 学什么：模型配置如何控制实验
- 看什么：`configs/models/openai_gpt4o.yaml`、`configs/models/openai_compatible_qwen.yaml`
- 动手做：解释 `temperature / top_p / max_tokens / timeout_seconds`
- 产出：配置参数说明表

### Day 31
- 学什么：单样本 smoke test 的意义
- 看什么：`scripts/smoke_test_tool_call.py`
- 动手做：运行 `python scripts/smoke_test_tool_call.py --help`
- 产出：解释这个脚本和 `run_batch.py` 的区别

### Day 32
- 学什么：环境变量和 API 密钥管理
- 看什么：`.env.example`
- 动手做：弄清 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPEN_MODEL_ENDPOINT` 的作用
- 产出：一页环境变量说明

### Day 33
- 学什么：模型输出的结构化解析
- 看什么：`runner/client.py`
- 动手做：解释 `tool_calls[0]`、`json.loads(arguments)`、`parse_error`
- 产出：一页结构化输出解析笔记

### Day 34
- 学什么：为什么要保留 `raw_response`
- 动手做：结合研究场景写出 3 个保留原始响应的理由
- 产出：一页“排错视角下的 raw_response”

### Day 35
- 学什么：本周复盘
- 动手做：不看代码，讲清一次 tool calling 请求从输入到结构化结果经历了什么
- 产出：一份 5 分钟口头讲稿

## 第 6 周：开始具备“能改项目”的能力

### Day 36
- 学什么：资产校验逻辑
- 看什么：`scripts/validate_assets.py`、`scripts/validate_phase3_assets.py`
- 动手做：解释为什么 Phase 2 和 Phase 3 要分开校验
- 产出：一份校验脚本对照说明

### Day 37
- 学什么：任务设计中的平衡性问题
- 看什么：`tasks/base_tasks_v1/*.json`
- 动手做：统计每个工具对应多少 task
- 产出：一张 task 分布表

### Day 38
- 学什么：版本冻结思想
- 看什么：`tool_v1`、`task_v1`、`prompt_v1`
- 动手做：写一段说明为什么研究仓库不应该随手覆盖旧版本
- 产出：一页版本管理笔记

### Day 39
- 学什么：如何增加一个新任务
- 动手做：仿照现有格式，给某个工具加 1 条新 task
- 产出：你自己写的 1 条 task

### Day 40
- 学什么：如何增加一个新变体
- 动手做：给你昨天写的 task 补齐四类变体
- 产出：完整变体版本

### Day 41
- 学什么：如何用脚本检查自己加的资产没有破坏系统
- 动手做：再次运行 `python scripts/validate_assets.py`
- 产出：一份修改前后对照记录

### Day 42
- 学什么：本周复盘
- 动手做：总结“如果我要加一个工具或任务，需要改哪些地方”
- 产出：一张修改清单

## 第 7 周：补上论文与研究问题层面的理解

### Day 43
- 学什么：项目不是普通工程，它是研究项目
- 看什么：`paper/phase1/literature_review.csv`
- 动手做：看懂文献表字段是什么意思
- 产出：一页字段解释

### Day 44
- 学什么：研究空白是什么
- 看什么：`paper/phase1/research_gap_statement_cn.md`
- 动手做：把研究空白压缩成 3 句话
- 产出：你自己的 3 句版研究空白

### Day 45
- 学什么：研究边界是什么
- 看什么：`paper/phase1/research_boundary_statement_cn.md`
- 动手做：写出“这个项目不声称什么”
- 产出：一页边界说明

### Day 46
- 学什么：和当前项目最相关的 2 篇文献
- 看什么：`paper/phase1/reading_notes_index.md` 对应笔记
- 动手做：选 2 篇做精读
- 产出：2 篇精读摘要

### Day 47
- 学什么：再补 2 篇高相关文献
- 看什么：`paper/phase1/notes/*.md`
- 动手做：继续精读 2 篇
- 产出：2 篇精读摘要

### Day 48
- 学什么：为什么这个题不是单纯 benchmark
- 动手做：从“错误机制解释”“表征边界”“防御层”三个角度写 400 字
- 产出：一段研究定位说明

### Day 49
- 学什么：本周复盘
- 动手做：假设你要给导师讲 3 分钟，讲清为什么这个题值得做
- 产出：3 分钟发言稿

## 第 8 周：开始补表示学习和 Transformer 基础

### Day 50
- 学什么：token、tokenizer、embedding、hidden state、logits 的区别
- 动手做：分别给出通俗解释
- 产出：一张概念对照表

### Day 51
- 学什么：`transformers` 的基本使用方式
- 动手做：看懂 `AutoTokenizer` 和 `AutoModelForCausalLM` 在做什么
- 产出：一页基础 API 笔记

### Day 52
- 学什么：hidden states 为什么能用于边界分析
- 看什么：`boundary/export_hidden_states.py`
- 动手做：逐段解释脚本
- 产出：一页 `export_hidden_states.py` 解析

### Day 53
- 学什么：向量表示、余弦相似度
- 动手做：用你自己的话解释“语义接近”为什么能被向量近似表达
- 产出：一页 embedding 直觉说明

### Day 54
- 学什么：PCA 是什么
- 动手做：找一个小数据例子解释“降维但尽量保留信息”
- 产出：一页 PCA 笔记

### Day 55
- 学什么：UMAP 是什么，和 PCA 有什么不同
- 动手做：写一段比较说明
- 产出：PCA vs UMAP 对照表

### Day 56
- 学什么：边界样本是什么
- 动手做：从分类视角解释“靠近边界的样本更脆弱”
- 产出：一页边界样本说明

### Day 57
- 学什么：本周复盘
- 动手做：讲清“为什么这个项目后面要导 hidden states”
- 产出：一段 300 字解释

## 第 9 周：开始补统计和因果基础

### Day 58
- 学什么：相关不等于因果
- 动手做：自己举 3 个例子区分 correlation 和 causation
- 产出：一页例子说明

### Day 59
- 学什么：混杂变量、媒介变量、碰撞变量
- 动手做：结合本项目举例，比如语言、任务难度、工具组别
- 产出：一张因果角色表

### Day 60
- 学什么：DAG 的直觉
- 动手做：画一个最简单的项目因果草图
- 产出：一张 5 个节点以内的小图

### Day 61
- 学什么：PC 算法和 NOTEARS 在概念上做什么
- 动手做：先只理解输入、输出、作用，不追数学细节
- 产出：一页算法功能说明

### Day 62
- 学什么：bootstrap 和稳定性是什么意思
- 动手做：解释为什么研究里不能只跑一张图就下结论
- 产出：一页稳定性说明

### Day 63
- 学什么：显著性检验在这里为什么有用
- 动手做：理解“不是只看均值差”
- 产出：一页统计检验直觉笔记

### Day 64
- 学什么：本周复盘
- 动手做：写一页“如果我要做因果分析，当前项目至少需要哪些变量”
- 产出：一页变量列表

## 第 10 周：补特征工程和数据分析能力

### Day 65
- 学什么：什么是 feature schema
- 动手做：先给 10 条样本想 8~10 个特征
- 产出：一版小型特征表

### Day 66
- 学什么：四类特征：指令侧、工具侧、匹配侧、上下文侧
- 动手做：把昨天的特征归类
- 产出：一张特征分组表

### Day 67
- 学什么：`pandas` 在这个项目里主要怎么用
- 看什么：`scripts/build_phase3_processed.py`
- 动手做：练习把任务或标签整理成 DataFrame
- 产出：一个你自己生成的小表格

### Day 68
- 学什么：缺失值、异常值、标签泄漏
- 动手做：举 3 个“看起来像特征但其实不能用”的例子
- 产出：一页特征风险说明

### Day 69
- 学什么：数据划分为什么要按 intent / family，而不是乱随机
- 看什么：`engineering_plan_cn.md` 里 Phase 3、`data/processed/split.csv`
- 动手做：写一段 split 设计说明
- 产出：一页划分原则

### Day 70
- 学什么：标注规范和数据卡
- 看什么：`data/annotations/annotation_guideline.md`、`data/processed/data_card.md`
- 动手做：自己给这个项目起草一个迷你版 `annotation guideline`
- 产出：一页标注规范草稿

### Day 71
- 学什么：本周复盘
- 动手做：写一页“如果让我做 Phase 3，我第一周会先做什么”
- 产出：你的 Phase 3 启动清单

## 第 11 周：把防御系统为什么存在想清楚

### Day 72
- 学什么：为什么这个项目最后不止要分析，还要做 defense
- 看什么：`engineering_plan_cn.md` 里 Phase 5
- 动手做：写出“解释”和“防御”之间的关系
- 产出：一页 defense 定位说明

### Day 73
- 学什么：澄清模块的逻辑
- 动手做：给 10 个工具各写 1 条澄清问句模板
- 产出：一份澄清模板表

### Day 74
- 学什么：工具描述增强的逻辑
- 动手做：找出最容易混淆的 3 对工具，并写“该用 / 不该用”边界
- 产出：3 对工具边界说明

### Day 75
- 学什么：风险评分器的直觉
- 动手做：用规则法给 3 个风险档位设计触发条件
- 产出：一张风险分桶表

### Day 76
- 学什么：系统评估为什么不能只看降错率
- 动手做：解释误伤率、额外澄清轮数、延迟成本
- 产出：一页评估指标说明

### Day 77
- 学什么：残余失败分析
- 动手做：假设防御后仍失败，列出 5 类可能原因
- 产出：一份 residual failure taxonomy

### Day 78
- 学什么：本周复盘
- 动手做：讲清“如果我要做一个 defense wrapper，它应该输入什么、输出什么”
- 产出：一份 wrapper 接口草图

## 第 12 周：整合、输出、确认你真的学会了

### Day 79
- 学什么：把项目整体再走一遍
- 动手做：从 `README_CN.md` 开始重新梳理目录、脚本、runner、evaluator
- 产出：一张总览图

### Day 80
- 学什么：真正的掌握不是“看过”，而是“能自己讲清”
- 动手做：录一段 8 分钟讲解，主题是“SRTP 项目技术主链路”
- 产出：你的讲解稿

### Day 81
- 学什么：真正的掌握不是“能讲”，而是“能改”
- 动手做：自己做一个最小改动，比如新增一个 task 或新增一个 evaluator 测试
- 产出：一处你亲手完成的小修改

### Day 82
- 学什么：修改后的验证习惯
- 动手做：重新运行
  - `python scripts/validate_assets.py`
  - `python -m pytest tests/test_evaluator.py`
- 产出：一份“修改后验证记录”

### Day 83
- 学什么：研究型项目的最后一步是形成自己的表达
- 动手做：写一篇 800~1200 字总结，题目可以叫“我现在如何理解 SRTP 项目”
- 产出：你的项目总结文档

### Day 84
- 学什么：最终复盘
- 动手做：对照下面的清单逐条自测
- 产出：最终自评结果

---

## 6. 最终自测清单

如果下面大部分问题你都能独立回答，就算你已经“真正学会这个项目”了。

- 我能解释这个项目的研究目标是什么
- 我能解释为什么它不是普通的 Python 小项目
- 我能看懂 `tools/tool_schemas_v1.json`
- 我能看懂 `tasks/base_tasks_v1/*.json`
- 我能看懂 `runner/run_batch.py`
- 我能解释 `runner/client.py` 为什么要保留 `raw_response`
- 我能解释 `evaluator/rules.py` 的标签体系
- 我能自己补一条 task
- 我能自己补一个 evaluator 测试
- 我能说明为什么 Phase 3 要做外部验证集
- 我能说明为什么 Phase 4 既要做因果，也要做边界分析
- 我能说明 Phase 5 的 defense 是怎么从分析结果长出来的

## 7. 这 12 周里你最该优先学的知识顺序

如果你时间不够，按这个优先级学：

1. `Python 基础 + Path / json / yaml / argparse`
2. `仓库结构 + runner + evaluator`
3. `tool calling 基础`
4. `pydantic + pandas + pytest`
5. `Phase 3 任务池 / split / annotation guideline / processed data`
6. `embedding / hidden states / PCA / UMAP`
7. `统计基础 + 因果图直觉`
8. `防御系统设计`

## 9. 跟当前仓库配套的最短命令路径

如果你是照着“当前已经更新到 Phase 3 的仓库”来学，最短命令路径是：

```bash
conda activate srtp
python scripts/check_env.py
python scripts/validate_assets.py
python scripts/generate_phase3_assets.py
python scripts/build_phase3_processed.py
python scripts/validate_phase3_assets.py
python -m pytest tests/test_evaluator.py tests/test_phase3_assets.py
```

这几条命令通过之后，你就已经把当前仓库最重要的静态链路跑通了。

## 10. 对你最现实的建议

你现在最容易犯的错误不是“学得慢”，而是：

- 一上来就想把因果推断学很深
- 一上来就想把 Transformer 数学细节全啃完
- 还没跑通项目就急着看很多外部论文

对你来说，最优路径不是“先补全理论”，而是：

1. 先把当前仓库读懂
2. 先能跑、能改、能解释
3. 再去学更深的表示分析和因果分析

如果执行稳定，这个项目你在 `12 周左右` 可以学到“能独立继续做”的程度。  
如果只是想达到“我已经能跟着项目一起干活”，通常 `4~6 周` 就够。
