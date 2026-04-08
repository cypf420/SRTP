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

当前工作区尚未配置真实模型凭据，所以：

- `split.csv`
- `task_metadata.csv`
- `data_card.md`

已经完整生成；

而：

- `episodes.jsonl`
- `labels.csv`
- `run_metadata.csv`
- `boundary_subset.jsonl`

仍处于“结构已就绪，等待真实运行结果写入”的状态。
