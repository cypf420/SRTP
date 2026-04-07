# FAIL-TaLMs / Benchmarking Failures 阅读笔记

## 论文信息

- 标题：Benchmarking Failures in Tool-Augmented Language Models
- 年份：2025
- 会议：NAACL 2025
- 链接：https://aclanthology.org/2025.naacl-long.149.pdf

## 它研究什么

这篇工作非常关键，因为它不再只衡量成功率，而是系统研究 TaLM 的**失败状态**。公开摘要明确指出其 benchmark 聚焦两类问题：

- under-specified user queries
- non-available tools

这两类都和你要做的 wrong tool / parameter hallucination 机制分析直接相关。

## 为什么它重要

这篇论文最有价值的地方在于它把一个常被忽视的问题讲清楚了：

> 真实世界里，很多失败不是因为模型不会做“标准题”，而是因为输入信息本来就不完整，或者可用工具本来就不足。

如果模型在这些场景里仍继续执行，就非常容易出现：

- 错选一个“看起来最像”的工具
- 幻构参数
- 不报告失败
- 不发起澄清

## 对本项目的直接启发

1. 你的任务库必须显式包含 under-specified variants。
2. 你的 evaluator 必须能区分“正常调用错了”和“本应澄清却调用了”。
3. 你的防御模块不该只做参数校验，还要做**可解性 / 可执行性判断**。

## 它没有解决什么

1. 虽然它研究 failure state，但主要还是 benchmark，不是因果解释框架。
2. 没有系统回答哪些请求特征、工具特征和上下文特征在驱动这些 failure state。
3. 没有引入表示边界分析。

## 你可以怎么用

- 用它作为 Phase 3 任务扩展和标签细化的最直接依据。
- 用它支撑“为什么要把信息不足场景主动造出来”。
- 用它支撑“澄清行为是工具调用可靠性的核心指标之一”。
