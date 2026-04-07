# AgentDojo 阅读笔记

## 论文信息

- 标题：AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents
- 年份：2024
- 会议：arXiv preprint（后续有正式发表版本）
- 链接：https://arxiv.org/abs/2406.13352

## 它研究什么

这篇工作关注的是**工具型 agent 在不可信外部数据环境中的 prompt injection 脆弱性**。这和本项目的关系不在“你也要做攻击 benchmark”，而在于它说明：

> 工具调用错误不只是能力问题，也可能由上下文污染和注入式干扰诱发。

## 核心内容

根据论文摘要：

- 提供动态环境
- 评估 prompt injection attacks 和 defenses
- 包含 97 个真实任务、629 个 security test cases
- 任务横跨邮件、网银、旅行预订等真实工具环境

## 对本项目的价值

1. 它给了你“误导干扰型任务”的现实依据。
2. 它提醒你上下文侧特征不能缺位，例如：
   - 是否含有外部来源文本
   - 是否含有工具返回中的指令性内容
   - 是否存在与用户目标无关但带有强行动词的上下文
3. 它说明错误样本里有一部分是**被误导的错误**，不是纯粹能力不足。

## 它没有解决什么

1. 主要目标是安全鲁棒性评估，不是可解释因果发现。
2. 没有把 injection 诱发错误细化成 wrong tool / parameter hallucination 的统一标签体系。
3. 没有把安全评测结果转成轻量可部署的 pre-call wrapper。

## 你可以怎么用

- 在任务设计里加入“误导干扰型”变体时，用它作为现实动机。
- 在特征体系里加入上下文污染相关特征。
- 在论文讨论部分说明：你的方法既适用于一般模糊请求，也可作为注入诱发错误的前置分析层。
