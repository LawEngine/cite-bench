#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path
import sys

from tqdm import tqdm

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from citebench.datasets import load_public_dataset
from citebench.openai_runner import (
    RunConfig,
    build_default_audit_path,
    build_default_submission_path,
    run_benchmark,
)
from citebench.settings import (
    DEFAULT_CONCURRENCY,
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_MODEL,
    DEFAULT_REASONING_EFFORT,
    DEFAULT_SYSTEM_PROMPT_PATH,
    DEFAULT_USER_PROMPT_PATH,
    env_int,
    env_optional_float,
    env_text,
    load_local_env,
    load_prompt_text,
    resolve_public_dataset_path,
)


async def _main() -> None:
    parser = argparse.ArgumentParser(
        description="Run OpenAI against the public cite-bench dataset"
    )
    parser.add_argument("--input", type=Path, default=None, help="Public benchmark JSON")
    parser.add_argument("--output", type=Path, default=None, help="Submission CSV path")
    parser.add_argument("--audit", type=Path, default=None, help="Audit JSONL path")
    parser.add_argument("--model", default=None, help=f"Model to run (default: {DEFAULT_MODEL})")
    parser.add_argument(
        "--reasoning-effort",
        choices=["none", "low", "medium", "high", "xhigh"],
        default=None,
    )
    parser.add_argument("--concurrency", type=int, default=None)
    parser.add_argument("--max-output-tokens", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=None)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--system-prompt-file", type=Path, default=None)
    parser.add_argument("--user-prompt-file", type=Path, default=None)
    args = parser.parse_args()

    load_local_env()

    dataset_path = resolve_public_dataset_path(args.input)
    if not dataset_path.exists():
        raise SystemExit(f"Public dataset not found: {dataset_path}")
    cases = load_public_dataset(dataset_path)
    if args.limit > 0:
        cases = cases[: args.limit]

    model = args.model or env_text("OPENAI_DEFAULT_MODEL", DEFAULT_MODEL)
    reasoning_effort = args.reasoning_effort or env_text(
        "OPENAI_REASONING_EFFORT", DEFAULT_REASONING_EFFORT
    )
    concurrency = args.concurrency or env_int("OPENAI_CONCURRENCY", DEFAULT_CONCURRENCY)
    max_output_tokens = args.max_output_tokens or env_int(
        "OPENAI_MAX_OUTPUT_TOKENS", DEFAULT_MAX_OUTPUT_TOKENS
    )
    temperature = args.temperature if args.temperature is not None else env_optional_float(
        "OPENAI_TEMPERATURE"
    )
    system_prompt = load_prompt_text(args.system_prompt_file or DEFAULT_SYSTEM_PROMPT_PATH)
    user_prompt_template = load_prompt_text(args.user_prompt_file or DEFAULT_USER_PROMPT_PATH)

    output_path = (args.output or build_default_submission_path(model)).resolve()
    audit_path = (args.audit or build_default_audit_path(model)).resolve()

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is not set")

    print(f"Loaded {len(cases)} rows from {dataset_path}")
    print(f"Model: {model}")
    print(f"Reasoning effort: {reasoning_effort}")
    print(f"Concurrency: {concurrency}")
    print(f"Output: {output_path}")
    print(f"Audit: {audit_path}")
    print(f"System prompt: {args.system_prompt_file or DEFAULT_SYSTEM_PROMPT_PATH}")
    print(f"User prompt: {args.user_prompt_file or DEFAULT_USER_PROMPT_PATH}")
    print()

    progress = tqdm(total=len(cases), unit="case")

    def on_progress(done: int, total: int) -> None:
        progress.total = total
        progress.update(done - progress.n)

    try:
        summary = await run_benchmark(
            cases=cases,
            api_key=api_key,
            config=RunConfig(
                model=model,
                reasoning_effort=reasoning_effort,
                concurrency=concurrency,
                max_output_tokens=max_output_tokens,
                temperature=temperature,
                system_prompt=system_prompt,
                user_prompt_template=user_prompt_template,
            ),
            output_path=output_path,
            audit_path=audit_path,
            on_progress=on_progress,
        )
    finally:
        progress.close()

    print("Run complete")
    print(f"  Rows: {summary['rows_processed']}")
    print(f"  Time: {summary['elapsed_seconds']}s")
    print(f"  Input tokens: {summary['input_tokens']}")
    print(f"  Output tokens: {summary['output_tokens']}")
    print(f"  Predicted labels: {summary['predicted_status_counts']}")
    print()
    print("Official scoring is not included in this public repo.")
    print("Keep the submission CSV for the separate grading flow.")


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
