# Phase 1 阅读笔记索引

以下 5 篇笔记是当前最直接支撑本项目研究定位的核心文献。

1. [MetaTool Benchmark 笔记](./notes/01_metatool_benchmark.md)
2. [StableToolBench 笔记](./notes/02_stabletoolbench.md)
3. [ToolBeHonest 笔记](./notes/03_toolbehonest.md)
4. [FAIL-TaLMs / Benchmarking Failures 笔记](./notes/04_fail_talms.md)
5. [AgentDojo 笔记](./notes/05_agentdojo.md)

选择这 5 篇的原因：

- `MetaTool` 直接定义了“应不应该用工具、该选哪个工具”这一问题。
- `StableToolBench` 直接指出大规模 benchmark 本身会受环境不稳定影响。
- `ToolBeHonest` 直接聚焦 tool-augmented hallucination。
- `FAIL-TaLMs` 直接研究 under-specified query 和 unavailable tool 两类失败。
- `AgentDojo` 直接覆盖 tool-calling agent 在 prompt injection 下的安全脆弱性。
