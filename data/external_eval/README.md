# External Eval

本目录对应 Phase 3 的 external evaluation 说明。

## 当前资产

- 任务定义位于 `tasks/external_eval_v1/*.json`
- `data/processed/split.csv` 中这部分样本统一标记为 `external_eval`
- 当前 external_eval 共 `100` 条 task，展开为 `400` 条 sample variant

## 设计目标

- 不参与 prompt 调参
- 不参与规则打磨
- 不参与特征筛选
- 用于报告 held-out 风格结果

## 当前实现方式

这批 external_eval 样本来自主任务家族的风格改写与 held-out 实例扩展，重点是：

- 保留相同工具集合
- 保留 schema 约束
- 改写表达方式
- 使用未进入主任务池的补充实例

由于当前工作区还没有接入真实公开 benchmark 的自动导入流程，所以这部分更准确地说是“held-out realistic-style external set”，不是公开 benchmark 的直接子集。
