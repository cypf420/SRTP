# SRTP 期中提交实验附件

这份附件对应 2026 年 11 月 15 日期中提交版。Qwen2.5-7B 的 24 对单因素实验已完成。GLM-4.7 的历史数据保留，同协议的第二模型复验待补。[期中报告](../midterm_report_cn.md) · [PDF](../midterm_report_cn.pdf)

| 结果 | 数量和核对入口 |
| --- | --- |
| 主任务重评 | GLM-4.7 与 Qwen2.5-7B 各 1,000 条。[逐条标签对照](label_comparison.csv) · [汇总](label_comparison_summary.json) · [历史响应](../../data/raw_runs) |
| Qwen 配对实验 | 年份显式性与工具描述各 12 对，共 48 条响应。[冻结计划](interventions/plan.json) · [运行配置](interventions/qwen_config.json) · [原始响应](interventions/qwen.jsonl) · [逐对结果](interventions/pairs.json) · [汇总](interventions/summary.json) |
| 调用前特征 | 2,000 条运行记录及 20 列特征。[矩阵](features.csv) · [基线结果](feature_metrics.json) |
| 子代理补充试验 | 四批共 48 条文本判断。[批次输入与输出](interventions/subagent_pilot) · [逐条评分](interventions/subagent_pilot/scored_rows.json) · [汇总](interventions/subagent_pilot/summary.json) |

主任务按 `(run_id, sample_id)` 关联。配对实验按 `(group, case_id, arm)` 关联。子代理结果没有可核验的实际模型标识，单独作为补充材料。

## 从已保存的响应重算

在新克隆的仓库根目录安装项目依赖后运行下列 PowerShell 命令。命令读取历史响应并写出本地结果，无需模型凭据。

```powershell
python scripts/build_phase3_processed.py
python scripts/summarize_midterm_reassessment.py
python features/build_midterm_features.py
$source = 'paper/midterm_results/interventions'
$output = 'outputs/midterm/interventions'
New-Item -ItemType Directory -Force -Path $output | Out-Null
Copy-Item -LiteralPath "$source/plan.json", "$source/qwen.jsonl", "$source/glm_failure.json" -Destination $output
python scripts/run_midterm_interventions.py summarize
python -m pytest -q
python scripts/validate_assets.py
python scripts/validate_phase3_assets.py
```

重算文件位于 `data/processed/` 和 `outputs/midterm/`。如克隆目录已有自己跑出的结果，可换用空目录验证。
