from __future__ import annotations

import asyncio
import json
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Literal

from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from .datasets import BenchmarkCase, write_audit_jsonl, write_submission_csv
from .settings import (
    DEFAULT_CONCURRENCY,
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_MODEL,
    DEFAULT_REASONING_EFFORT,
    DEFAULT_SYSTEM_PROMPT_PATH,
    DEFAULT_USER_PROMPT_PATH,
    LABEL_SET,
    LABELS,
    default_output_dir,
    load_prompt_text,
)


class PredictionPayload(BaseModel):
    reasoning: str = Field(
        description="Brief step-by-step reasoning (2-4 sentences) before choosing a label.",
    )
    predicted_status: Literal[
        "VERIFIED",
        "NOT_FOUND",
        "MISATTRIBUTED",
        "CITATION_UNRESOLVED",
    ] = Field(description="The single correct verification label.")


PROMPT_TEMPLATE = load_prompt_text(DEFAULT_USER_PROMPT_PATH)
SYSTEM_PROMPT = load_prompt_text(
    DEFAULT_SYSTEM_PROMPT_PATH,
    fallback="You classify citation verification rows.",
)

STRICT_RETRY_TEMPLATE = """Your previous response did not validate.

Return a JSON object with two fields:
- "reasoning": 2-4 sentences of step-by-step analysis
- "predicted_status": exactly one of VERIFIED, NOT_FOUND, MISATTRIBUTED, CITATION_UNRESOLVED

Citation: {citation}
Quoted passage: {quote}
"""


@dataclass(slots=True)
class RunConfig:
    model: str = DEFAULT_MODEL
    reasoning_effort: str = DEFAULT_REASONING_EFFORT
    concurrency: int = DEFAULT_CONCURRENCY
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS
    temperature: float | None = None
    system_prompt: str = SYSTEM_PROMPT
    user_prompt_template: str = PROMPT_TEMPLATE


@dataclass(slots=True)
class CallResult:
    predicted_status: str
    reasoning: str
    raw_text: str
    input_tokens: int
    output_tokens: int
    request_id: str | None
    response_model: str | None
    latency_ms: float
    status: str | None
    incomplete_reason: str | None
    error: str | None
    attempts: int


def _model_slug(model: str) -> str:
    return model.replace("/", "_").replace(".", "_").replace(":", "_")


def build_default_submission_path(model: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return default_output_dir() / "submissions" / f"{stamp}_{_model_slug(model)}.csv"


def build_default_audit_path(model: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return default_output_dir() / "audit" / f"{stamp}_{_model_slug(model)}.jsonl"


def _should_send_reasoning(model: str) -> bool:
    return model.startswith("gpt-5")


def _effective_max_output_tokens(model: str, reasoning_effort: str, requested: int) -> int:
    if model.startswith("gpt-5"):
        floor_by_effort = {
            "none": 80,
            "low": 160,
            "medium": 384,
            "high": 768,
            "xhigh": 1200,
        }
        return max(requested, floor_by_effort.get(reasoning_effort, 256))
    return requested


def _normalize_prediction(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip().upper()
    return text if text in LABEL_SET else ""


def _parse_prediction(raw_text: str) -> tuple[str, str]:
    if not raw_text:
        return "", ""
    try:
        parsed = json.loads(raw_text)
    except Exception:
        return _normalize_prediction(raw_text), ""
    return (
        _normalize_prediction(parsed.get("predicted_status")),
        str(parsed.get("reasoning", "")),
    )


def _raw_text_from_response(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return str(output_text)

    output_parsed = getattr(response, "output_parsed", None)
    if output_parsed is not None:
        if hasattr(output_parsed, "model_dump_json"):
            return output_parsed.model_dump_json()
        try:
            return json.dumps(output_parsed, ensure_ascii=False)
        except Exception:
            return str(output_parsed)

    return ""


async def _call_openai(
    client: AsyncOpenAI,
    *,
    model: str,
    system_prompt: str,
    prompt: str,
    reasoning_effort: str,
    max_output_tokens: int,
    temperature: float | None,
) -> CallResult:
    request: dict[str, Any] = {
        "model": model,
        "store": False,
        "max_output_tokens": max_output_tokens,
        "input": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    }

    if _should_send_reasoning(model):
        request["reasoning"] = {"effort": reasoning_effort}

    if temperature is not None:
        safe_temperature = not (model.startswith("gpt-5") and reasoning_effort != "none")
        if safe_temperature:
            request["temperature"] = temperature

    started = time.monotonic()
    response = await client.responses.parse(**request, text_format=PredictionPayload)
    latency_ms = (time.monotonic() - started) * 1000.0

    output_parsed = getattr(response, "output_parsed", None)
    predicted_status = _normalize_prediction(
        getattr(output_parsed, "predicted_status", None)
    )
    reasoning = str(getattr(output_parsed, "reasoning", "") or "")
    raw_text = _raw_text_from_response(response)

    if not predicted_status:
        predicted_status, reasoning = _parse_prediction(raw_text)

    usage = getattr(response, "usage", None)
    input_tokens = int(getattr(usage, "input_tokens", 0) or 0)
    output_tokens = int(getattr(usage, "output_tokens", 0) or 0)

    incomplete_reason = None
    incomplete_details = getattr(response, "incomplete_details", None)
    if incomplete_details is not None:
        incomplete_reason = getattr(incomplete_details, "reason", None)
        if incomplete_reason is None and isinstance(incomplete_details, dict):
            incomplete_reason = incomplete_details.get("reason")

    return CallResult(
        predicted_status=predicted_status,
        reasoning=reasoning,
        raw_text=raw_text,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        request_id=getattr(response, "_request_id", None),
        response_model=getattr(response, "model", None),
        latency_ms=latency_ms,
        status=getattr(response, "status", None),
        incomplete_reason=incomplete_reason,
        error=None,
        attempts=1,
    )


async def _classify_case(
    client: AsyncOpenAI,
    case: BenchmarkCase,
    config: RunConfig,
) -> CallResult:
    prompt = config.user_prompt_template.format(
        citation=case.citation,
        quote=case.quote,
    )
    effective_max_output_tokens = _effective_max_output_tokens(
        config.model, config.reasoning_effort, config.max_output_tokens
    )
    attempts = 0
    last_result: CallResult | None = None
    current_prompt = prompt
    current_reasoning_effort = config.reasoning_effort
    current_max_output_tokens = effective_max_output_tokens

    for attempt in range(1, 4):
        attempts = attempt
        try:
            result = await _call_openai(
                client,
                model=config.model,
                system_prompt=config.system_prompt,
                prompt=current_prompt,
                reasoning_effort=current_reasoning_effort,
                max_output_tokens=current_max_output_tokens,
                temperature=config.temperature,
            )
        except Exception as exc:  # pragma: no cover - network/runtime path
            last_result = CallResult(
                predicted_status="",
                reasoning="",
                raw_text="",
                input_tokens=0,
                output_tokens=0,
                request_id=None,
                response_model=None,
                latency_ms=0.0,
                status="error",
                incomplete_reason=None,
                error=str(exc),
                attempts=attempt,
            )
            if attempt < 3:
                await asyncio.sleep(float(2 ** (attempt - 1)))
            continue

        result.attempts = attempt
        if result.predicted_status:
            return result

        last_result = result

        if (
            result.incomplete_reason == "max_output_tokens"
            and config.model.startswith("gpt-5")
            and current_reasoning_effort != "none"
        ):
            current_reasoning_effort = "none"
            current_max_output_tokens = max(current_max_output_tokens, 256)
        else:
            current_prompt = STRICT_RETRY_TEMPLATE.format(
                citation=case.citation,
                quote=case.quote,
            )
            current_max_output_tokens = max(current_max_output_tokens, 256)

        if attempt < 3:
            await asyncio.sleep(float(2 ** (attempt - 1)))

    if last_result is None:
        raise RuntimeError("classification failed without any attempts")
    last_result.attempts = attempts

    if not last_result.predicted_status:
        last_result.predicted_status = "VERIFIED"
    return last_result


async def run_benchmark(
    *,
    cases: list[BenchmarkCase],
    api_key: str,
    config: RunConfig,
    output_path: Path,
    audit_path: Path,
    on_progress: Callable[[int, int], None] | None = None,
) -> dict[str, Any]:
    if config.concurrency < 1:
        raise ValueError("concurrency must be at least 1")

    client = AsyncOpenAI(api_key=api_key)
    semaphore = asyncio.Semaphore(config.concurrency)
    started = time.monotonic()
    ordered_rows: list[dict[str, str] | None] = [None] * len(cases)
    ordered_audit: list[dict[str, Any] | None] = [None] * len(cases)
    total_input_tokens = 0
    total_output_tokens = 0
    completed = 0

    async def process(index: int, case: BenchmarkCase) -> tuple[int, CallResult]:
        async with semaphore:
            return index, await _classify_case(client, case, config)

    tasks = [asyncio.create_task(process(index, case)) for index, case in enumerate(cases)]
    for task in asyncio.as_completed(tasks):
        index, result = await task
        case = cases[index]
        ordered_rows[index] = {
            "id": case.id,
            "predicted_status": result.predicted_status,
        }
        ordered_audit[index] = {
            "id": case.id,
            "citation": case.citation,
            "quote": case.quote,
            "requested_model": config.model,
            "response_model": result.response_model,
            "predicted_status": result.predicted_status,
            "reasoning": result.reasoning,
            "raw_response": result.raw_text,
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "request_id": result.request_id,
            "latency_ms": round(result.latency_ms, 1),
            "status": result.status,
            "incomplete_reason": result.incomplete_reason,
            "error": result.error,
            "attempts": result.attempts,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        total_input_tokens += result.input_tokens
        total_output_tokens += result.output_tokens
        completed += 1
        if on_progress is not None:
            on_progress(completed, len(cases))

    submission_rows = [row for row in ordered_rows if row is not None]
    audit_rows = [row for row in ordered_audit if row is not None]
    write_submission_csv(submission_rows, output_path)
    write_audit_jsonl(audit_rows, audit_path)

    predicted_counts = Counter(
        row["predicted_status"] or "EMPTY" for row in submission_rows  # type: ignore[index]
    )
    elapsed = max(time.monotonic() - started, 1e-9)
    return {
        "requested_model": config.model,
        "reasoning_effort": config.reasoning_effort,
        "rows_processed": len(submission_rows),
        "elapsed_seconds": round(elapsed, 2),
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "concurrency": config.concurrency,
        "max_output_tokens": _effective_max_output_tokens(
            config.model, config.reasoning_effort, config.max_output_tokens
        ),
        "output_path": str(output_path),
        "audit_path": str(audit_path),
        "predicted_status_counts": dict(sorted(predicted_counts.items())),
    }
