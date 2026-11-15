# Phase 3 Data Card

## 1. 数据集名称

SRTP Tool-Calling Failure Analysis Dataset, Phase 3 Build

## 2. 数据用途

本数据集用于研究大模型在工具调用中的：

- 错误工具选择
- 参数幻构
- 本应澄清却直接调用
- 高风险工具误用

## 3. 组成概况

- 主任务池：`250` 条 task
- external_eval：`100` 条 task
- 总 task 数：`350`
- 每条 task 含四类 variant：
  - `clear`
  - `ambiguous`
  - `incomplete`
  - `misleading`
- 总 sample variant 数：`1400`

## 4. 工具覆盖

共 `10` 个工具，每个工具：

- 主任务池 `25` 条
- external_eval `10` 条

## 5. 语言覆盖

- 主任务池：`zh=140`，`en=110`
- external_eval：`zh=56`，`en=44`

## 6. 划分策略

主任务池按 `template_family` 划分：

- `train=150` tasks
- `dev=50` tasks
- `test=50` tasks

external_eval 单独保留：

- `external_eval=100` tasks

## 7. 数据来源

当前版本主要来自：

- Phase 2 的 `50` 条 base task family
- 基于 family 结构做的受控扩展
- held-out 风格的 external_eval 扩展

## 8. 标注方式

- gold tool / gold params 为规则化构造标签
- 运行后标签由自动评估器初判
- 人工复核规范见 `data/annotations/annotation_guideline.md`
- 争议样本记录到 `data/annotations/adjudication.csv`

## 9. 已知局限

- 主任务有 GLM-4.7 和 Qwen2.5-7B 各 1,000 条运行记录。每个模型运行同一批样本 ID，保留自动标签，人工仲裁待完成。
- `external_eval` 为同家族留出实例，和主任务共享模板家族，尚无运行结果。
- 数据仍然以模板化构造为主，适合机制分析，不应过度外推到所有 agent 场景

## 10. 后续更新条件

人工仲裁和评估规则冻结后，补齐留出集采集，并分别报告主任务家族切分和留出实例的结果。期中复核与基线见[期中报告](../../paper/midterm_report_cn.md)。
