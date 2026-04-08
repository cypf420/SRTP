from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ParameterSpec(BaseModel):
    type: Literal["string", "integer", "number", "boolean"]
    description: str
    grounded: bool = True
    enum: Optional[List[str]] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None


class ToolSchema(BaseModel):
    name: str
    group: str
    version: str
    risk_level: Literal["low", "medium", "high"]
    description: str
    confusion_with: List[str] = Field(default_factory=list)
    required: List[str] = Field(default_factory=list)
    parameters: Dict[str, ParameterSpec]
    examples: List[Dict[str, Any]] = Field(default_factory=list)


class TaskVariant(BaseModel):
    utterance: str
    need_clarification: bool = False
    clarification_fields: List[str] = Field(default_factory=list)


class TaskTemplate(BaseModel):
    task_id: str
    version: str = "task_v1"
    template_family: Optional[str] = None
    task_set: str = "main"
    intent: str
    domain: str
    language: Literal["zh", "en"]
    dialog_context: List[Dict[str, str]] = Field(default_factory=list)
    gold_tool: str
    gold_params: Dict[str, Any]
    distractor_tools: List[str] = Field(default_factory=list)
    variants: Dict[str, TaskVariant]
    notes: Optional[str] = None


class ModelConfig(BaseModel):
    backend: Literal["openai_chat"]
    model_name: str
    api_key_env: str
    base_url_env: Optional[str] = None
    temperature: float = 0.0
    top_p: float = 1.0
    max_tokens: int = 512
    timeout_seconds: int = 60
    support_tool_calling: bool = True


class RunConfig(BaseModel):
    run_name: str
    model_config_path: str
    tools_path: str
    tasks_glob: str
    prompt_path: str
    output_dir: str
    variant_names: List[str] = Field(default_factory=lambda: ["clear"])
    task_limit: Optional[int] = None
    seed: int = 42
    overwrite: bool = False


class PredictionRecord(BaseModel):
    tool_name_pred: Optional[str] = None
    arguments_pred: Dict[str, Any] = Field(default_factory=dict)
    raw_response: Any = None
    parse_error: Optional[str] = None


class EpisodeRecord(BaseModel):
    run_id: str
    sample_id: str
    task_id: str
    variant_name: str
    model_name: str
    prompt_version: str
    tool_version: str
    task_version: str
    messages: List[Dict[str, str]]
    tools: List[str]
    prediction: PredictionRecord
    latency_ms: int
    usage: Dict[str, Any] = Field(default_factory=dict)
