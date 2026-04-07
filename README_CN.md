# SRTP 工具调用失败分析

本仓库不是一个成品应用，而是一个**研究实验仓库**。  
它当前的目标是研究：

- 大模型在 `tool calling / function calling` 时为什么会选错工具
- 为什么会在参数里“脑补”并不存在的值
- 这些错误能不能用可解释特征、因果分析和轻量防御模块来解释与缓解

目前仓库已经完成了研究计划中的 **Phase 1** 和 **Phase 2**，也就是：

- 研究定位材料已经整理出来
- 最小实验框架已经搭好
- 10 个工具 schema 已定义
- 50 个 base task 已整理
- runner / evaluator / 校验脚本已经写好

但要注意：

- 现在仓库里**还没有正式跑出真实模型数据**
- 原因不是代码没写，而是当前还没有稳定配置好模型凭据与真实运行入口

所以你可以把这个仓库理解成：

> **“研究框架和实验底座已经搭好，接下来只差接入模型并正式跑实验。”**

## 你现在最需要知道的三件事

### 1. 这个仓库主要是 Python 项目

是的，当前绝大多数代码都是 Python。

所以推荐用 `conda` 虚拟环境，而不是直接在 `base` 环境里装依赖。原因很简单：

- 依赖较多，包含 `torch`、`transformers`、`sentence-transformers`、`causal-learn`
- 这些包在独立环境里更稳定
- 后面如果你要切换 Python 版本、重装依赖或迁移机器，成本更低

### 2. 推荐的运行环境是 `conda`

推荐环境名是：

```bash
srtp
```

如果你已经创建过，就直接：

```bash
conda activate srtp
```

### 3. “快速开始”不是让你一次把所有命令都跑完

之前不清楚的地方就在这里。

这些命令不是一个必须从上跑到下的流水线，而是分成三种用途：

- **第一次配置环境**
- **检查仓库本身是否正常**
- **真正开始跑模型实验**

下面我按这三种用途重新写。

---

## 仓库里有什么

### 研究材料

- `engineering_plan_cn.md`
  研究计划总表
- `research_report_cn.md`
  研究报告与路线图
- `paper/phase1/`
  文献表、阅读笔记、研究空白声明、研究边界说明

### 实验资产

- `tools/`
  工具 schema
- `tasks/`
  任务模板
- `prompts/`
  Prompt 模板
- `configs/`
  模型配置和运行配置

### 运行代码

- `runner/`
  模型调用与批量运行
- `evaluator/`
  自动评估逻辑
- `scripts/`
  环境检查、静态校验、smoke test
- `tests/`
  evaluator 测试

---

## 第一次配置环境

如果你是第一次在这台机器上跑这个仓库，先做这一段。

### 第 1 步：创建 conda 环境

```bash
conda env create -f environment.yml
```

这一步会做什么：

- 创建一个名为 `srtp` 的 conda 环境
- 安装 `environment.yml` 里定义的 Python 版本和依赖
- 再通过 `pip` 安装 `requirements.txt` 和 `requirements-dev.txt` 中的包

### 第 2 步：激活环境

```bash
conda activate srtp
```

这一步之后，你后面的 Python 命令都应该默认在 `srtp` 环境里执行。

### 第 3 步：复制环境变量模板

```bash
copy .env.example .env
```

这一步会做什么：

- 把环境变量模板复制成你本地可编辑的 `.env`
- 后面如果要接 OpenAI API 或本地模型服务，就在这里填配置

如果你只是想先看框架是否正常，这一步可以先做，但里面暂时不填也行。

---

## 先检查仓库是否正常

这一段的目标不是跑模型，而是确认：

- 依赖装好了没有
- 工具和任务文件是不是完整
- evaluator 有没有明显问题

### 1. 检查 Python 依赖是否能正常导入

```bash
python scripts/check_env.py
```

这一步会做什么：

- 检查关键 Python 包能不能正常 import
- 比如 `openai`、`pandas`、`pydantic`、`yaml` 等

如果它通过，说明环境大体没坏。

### 2. 检查仓库里的静态实验资产是否完整

```bash
python scripts/validate_assets.py
```

这一步会做什么：

- 检查当前是否真的有 `10` 个工具 schema
- 检查当前是否真的有 `50` 个 base task
- 检查每个 task 是否都带了 `clear / ambiguous / incomplete / misleading` 四类变体

如果它通过，说明实验数据骨架是完整的。

### 3. 运行 evaluator 的单元测试

```bash
python -m pytest tests/test_evaluator.py
```

这一步会做什么：

- 测试 evaluator 的基础判断逻辑
- 比如：
  - 正常预测是否被标成 `correct`
  - 本应澄清却调用工具是否被识别
  - grounded 参数值错误是否被识别为 hallucination

如果这一步通过，说明评估器的最基础规则没有明显坏掉。

---

## 真正开始跑模型之前，要先准备什么

如果你想开始真正跑实验，而不是只做静态检查，那么你还需要模型入口。

当前仓库支持的方向是：

- OpenAI 风格的 API
- 本地或远端的 OpenAI-compatible 模型接口
- 后续可扩展到开源模型 hidden-state 导出

你至少要准备下面其中一种：

### 方案 A：OpenAI API

在 `.env` 里填：

```bash
OPENAI_API_KEY=...
OPENAI_BASE_URL=...
```

### 方案 B：本地或远端 OpenAI-compatible 模型服务

在 `.env` 里填：

```bash
OPEN_MODEL_ENDPOINT=...
OPEN_MODEL_NAME=...
```

如果这一步没配好，后面的 runner 能加载，但真实调用不会成功。

---

## 如何跑一个最小样本

如果你不想一上来就跑整批任务，先跑一条 smoke test：

```bash
python scripts/smoke_test_tool_call.py --model-config configs/models/openai_gpt4o.yaml
```

这一步会做什么：

- 读取一个模型配置
- 读取工具 schema
- 读取任务模板
- 默认挑一条 task 跑一次 tool calling
- 打印预测的工具名、参数、延迟和 usage

它的作用是：

- 先确认“模型调用链路通了”
- 不要一上来就跑批量任务然后半路才发现 API 配错了

---

## 如何跑一批样本

确认 smoke test 正常后，再跑 batch：

```bash
python runner/run_batch.py --config configs/runs/sample_run_v1.yaml
```

这一步会做什么：

- 读取运行配置
- 读取模型配置
- 读取工具 schema
- 读取任务模板
- 按配置批量调用模型
- 为这次运行自动生成一个 `run_id`
- 把输出写到 `data/raw_runs/<run_id>/`

你会在输出目录里看到至少这些文件：

- `episodes.jsonl`
  每条样本的原始运行结果
- `run_manifest.json`
  本次运行的元信息
- `run_config_snapshot.yaml`
  本次运行配置快照
- `model_config_snapshot.yaml`
  模型配置快照
- `system_prompt_snapshot.txt`
  Prompt 快照

这一步的目的，是把真实 tool-calling 结果落盘，供后续 evaluator、特征提取和因果分析使用。

---

## 一句话理解每条常用命令

如果你只想知道“我到底该跑哪个命令”，看这段就够了。

### 我只想确认 conda 环境没问题

```bash
conda activate srtp
python scripts/check_env.py
```

### 我只想确认仓库里的工具和任务资产没坏

```bash
conda activate srtp
python scripts/validate_assets.py
```

### 我只想确认 evaluator 正常

```bash
conda activate srtp
python -m pytest tests/test_evaluator.py
```

### 我想先试一条真实模型调用

```bash
conda activate srtp
python scripts/smoke_test_tool_call.py --model-config configs/models/openai_gpt4o.yaml
```

### 我想正式跑一小批实验

```bash
conda activate srtp
python runner/run_batch.py --config configs/runs/sample_run_v1.yaml
```

---

## 当前状态说明

当前仓库的状态是：

- 研究框架已经搭好
- 静态资产已经准备好
- 基础 runner 和 evaluator 已写好
- conda 环境已可用
- 但正式实验结果还没有开始大规模产出

所以你接下来最合理的动作是：

1. 激活 `srtp` 环境
2. 确认模型凭据
3. 先跑一条 smoke test
4. 再跑一批样本

## 相关文件

- 英文 README：[README.md](./README.md)
- 研究计划：[engineering_plan_cn.md](./engineering_plan_cn.md)
- 研究报告：[research_report_cn.md](./research_report_cn.md)
