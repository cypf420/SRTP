# StableToolBench 阅读笔记

## 论文信息

- 标题：StableToolBench: Towards Stable Large-Scale Benchmarking on Tool Learning of Large Language Models
- 年份：2024
- 会议：Findings of ACL 2024
- 链接：https://aclanthology.org/2024.findings-acl.664/

## 它研究什么

这篇工作关注 benchmark 本身的一个关键现实问题：**大规模 API benchmark 往往不稳定**。如果底层工具环境、API 返回或执行链波动很大，那么模型评估结果也会不稳。

## 核心贡献

- 提出 StableToolBench
- 讨论 API simulator、缓存系统和 evaluator 系统
- 强调 benchmarking 的可重复性与稳定性

## 对本项目为什么重要

你的项目虽然不是复刻 StableToolBench，但它提醒了一个很关键的工程原则：

> 如果评测环境不稳定，那么后续的“错误分析”“因果图”“关键因子”都可能建立在噪声上。

这和你现在的工程计划高度一致，特别对应以下动作：

- 冻结 `tool_v1` / `task_v1` / `prompt_v1`
- 保存运行元信息
- 区分正式结果和调试结果
- 固化 split
- 做 bootstrap 稳定性统计

## 它最值得借鉴的地方

1. 把 benchmark 的稳定性本身当成一等问题，而不是默认条件。
2. 强调 evaluator 和执行环境要一起设计。
3. 强调缓存、模拟器、标准化运行元数据的必要性。

## 它没有解决什么

1. 它解决的是 benchmark 稳定性，不是 failure mechanism。
2. 没有明确研究 wrong tool 和 parameter hallucination 的细粒度因果来源。
3. 没有把稳定评测进一步转化为解释或防御。

## 你可以怎么用

- 在论文方法部分，用它论证为什么你要记录配置快照、运行元信息、数据划分和 evaluator 版本。
- 在局限性部分，用它说明若环境不稳定，因果分析结论会被污染。
- 在工程实现上，把它作为“为什么 Phase 0 / Phase 2 要先做可复现实验底座”的依据。
