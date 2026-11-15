# Processed Data

本目录存放 Phase 3 的标准化数据文件。

## 当前文件

- `split.csv`
  - task 级别划分表
  - 字段：`task_id`, `template_family`, `task_set`, `split`, `language`, `domain`, `gold_tool`, `intent`
- `task_metadata.csv`
  - sample 级别元数据表
  - 一行对应一个 `task_id__variant`
- `episodes.jsonl`
  - 合并后的原始运行结果
  - 当前如果没有真实模型运行，则为空文件
- `labels.csv`
  - 自动评估结果
  - 当前如果没有真实模型运行，则只有表头
- `run_metadata.csv`
  - 运行级元信息
  - 当前如果没有真实模型运行，则只有表头
- `boundary_subset.jsonl`
  - 用于 hidden-state / 边界分析的样本子集
  - 当前如果没有开源模型运行，则为空文件
- `data_card.md`
  - 数据卡与局限说明

## 生成方式

先生成任务资产：

```bash
python scripts/generate_phase3_assets.py
```

再生成 processed 元数据：

```bash
python scripts/build_phase3_processed.py
```

## 说明

当前包含 GLM-4.7 与 Qwen2.5-7B 的 2,000 条主任务运行记录、2,000 条自动标签、2 条运行元数据和 1,000 条 Qwen 表征分析的输入记录。模型共享任务样本 ID，跨文件关联运行结果时使用 `(run_id, sample_id)`。留出集已有任务定义和元数据，采集尚待完成。
