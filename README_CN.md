# SRTP 工具调用失败分析

本仓库不是成品应用，而是一个研究实验仓库。  
当前研究目标是：

- 大模型为什么会选错工具
- 为什么会在参数里幻构不存在的值
- 这些错误能不能通过可解释特征、因果分析和轻量防御模块被解释与缓解

## 当前做到哪一步了

已经完成：

- Phase 1：文献摸底、研究空白和研究边界
- Phase 2：工具 schema、50 个 base task、prompt、runner、evaluator
- Phase 3：扩展任务池、external eval、split 元数据、标注规范、processed 数据构建管线

还没完成：

- 真实模型批量跑数
- 真正的 `episodes.jsonl`
- 真正的 `labels.csv`
- 真正的 `run_metadata.csv`
- 真正的 `boundary_subset.jsonl`

原因不是代码没写，而是这台机器现在还没有：

- `GLM_API_KEY`
- `OPEN_MODEL_API_KEY`
- `OPEN_MODEL_ENDPOINT`
- `LOCAL_HF_MODEL_ID`

所以你可以把当前状态理解成：

> **Phase 1~3 的静态资产已经齐了，真实模型结果只差凭据和跑数。**

## Phase 3 新增了什么

- `tasks/phase3_tasks_v1/`
  - `250` 条主任务
- `tasks/external_eval_v1/`
  - `100` 条 held-out external eval 任务
- `data/annotations/annotation_guideline.md`
- `data/annotations/adjudication.csv`
- `data/processed/split.csv`
- `data/processed/task_metadata.csv`
- `data/processed/data_card.md`
- `scripts/generate_phase3_assets.py`
- `scripts/build_phase3_processed.py`
- `scripts/validate_phase3_assets.py`
- `configs/runs/phase3_*.yaml`

## 仓库结构怎么理解

- `paper/phase1/`
  - 文献表、阅读笔记、研究定位材料
- `tools/`
  - 工具 schema
- `tasks/base_tasks_v1/`
  - Phase 2 的 50 条 seed task
- `tasks/phase3_tasks_v1/`
  - Phase 3 主任务池
- `tasks/external_eval_v1/`
  - Phase 3 的 held-out external eval 任务
- `prompts/`
  - Prompt 模板
- `runner/`
  - 模型调用与批量执行
- `evaluator/`
  - 自动评估规则
- `data/annotations/`
  - 标注规范与争议样本模板
- `data/processed/`
  - split、metadata、data card、以及后续合并结果
- `scripts/`
  - 检查、生成、验证脚本
- `configs/runs/`
  - 运行配置

## 第一次该跑什么

先激活 conda 环境：

```bash
conda activate srtp
```

先确认环境和 Phase 2 没坏：

```bash
python scripts/check_env.py
python scripts/validate_assets.py
python -m pytest tests/test_evaluator.py
```

再确认 Phase 3 资产完整：

```bash
python scripts/generate_phase3_assets.py
python scripts/build_phase3_processed.py
python scripts/validate_phase3_assets.py
python -m pytest tests/test_phase3_assets.py
```

如果这些都通过，说明：

- 主任务池已经生成
- external eval 已生成
- `split.csv` 和 `task_metadata.csv` 已经落盘
- Phase 3 的静态数据资产是完整的

## 真正开始跑实验时怎么做

你把模型凭据配好后，直接跑：

```bash
python runner/run_batch.py --config configs/runs/phase3_glm_main.yaml
python runner/run_batch.py --config configs/runs/phase3_qwen_main.yaml
python runner/run_batch.py --config configs/runs/phase3_glm_external_eval.yaml
python runner/run_batch.py --config configs/runs/phase3_qwen_external_eval.yaml
python scripts/build_phase3_processed.py
```

这一步会把真实运行结果合并回：

- `data/raw_runs/<run_id>/...`
- `data/processed/episodes.jsonl`
- `data/processed/labels.csv`
- `data/processed/run_metadata.csv`
- `data/processed/boundary_subset.jsonl`

## 现在你最该知道的事实

- `data/processed/split.csv` 和 `data/processed/task_metadata.csv` 已经是正式资产
- `episodes.jsonl`、`labels.csv`、`run_metadata.csv`、`boundary_subset.jsonl` 目前还是“结构已准备好，但没有真实模型结果”
- external eval 当前是 held-out realistic-style 集，不是公开 benchmark 的直接切分
- 当前推荐的模型组合是 `GLM-4.7 + Qwen2.5-7B-Instruct`
