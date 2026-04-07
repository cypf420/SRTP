# ToolBeHonest 阅读笔记

## 论文信息

- 标题：ToolBeHonest: A Multi-level Hallucination Diagnostic Benchmark for Tool-Augmented Large Language Models
- 年份：2024
- 会议：EMNLP 2024
- 链接：https://aclanthology.org/2024.emnlp-main.637/

## 它研究什么

这篇工作是当前与你课题最接近的文献之一，因为它不再只问“工具用得对不对”，而是明确聚焦**tool-augmented hallucination**。

## 数据和任务

根据论文公开摘要，这个 benchmark：

- 采用多层级诊断流程
- 覆盖 solvability detection、solution planning、missing-tool analysis
- 构造了 700 条人工标注样本
- 覆盖 missing tools、potential tools、limited functionality tools 等场景

## 关键发现

1. 即使强模型，在工具场景中也会出现严重 hallucination。
2. 更大的模型参数并不自动意味着更少 hallucination。
3. 关键问题之一是模型对“当前任务是否可解”的判断能力不足。

## 对本项目的价值

这篇论文直接说明了一个非常重要的点：

> parameter hallucination 往往不是孤立现象，它和“可解性判断错误”“缺工具时继续硬做”“缺参数时不澄清”是连在一起的。

这对你后续标签体系和因果图设计很重要，因为它暗示你不能只做一个粗糙的 `param_error` 标签，而要把：

- missing required information
- should clarify but called
- missing tool but forced execution
- grounded value hallucination

这些 failure state 细分出来。

## 它没有解决什么

1. 主要诊断 hallucination，没有系统做因果结构学习。
2. 没有把错误映射到一组稳定的人工可读因子。
3. 没有把诊断结果直接转成防御 wrapper。

## 你可以怎么用

- 作为“为什么参数幻构值得单独研究”的核心文献。
- 作为你扩展细粒度错误标签和 `should_clarify_but_called` 标签的依据。
- 作为防御模块里“先判断是否可解/是否缺关键参数”的直接灵感来源。
