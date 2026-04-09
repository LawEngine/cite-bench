from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None


ROOT_DIR = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT_DIR / "prompts"

PUBLIC_JSON_NAME = "cite-bench-v1.json"

LABELS = (
    "VERIFIED",
    "NOT_FOUND",
    "MISATTRIBUTED",
    "CITATION_UNRESOLVED",
)
LABEL_SET = set(LABELS)

DEFAULT_MODEL = "gpt-5.4-mini"
DEFAULT_REASONING_EFFORT = "xhigh"
DEFAULT_CONCURRENCY = 20
DEFAULT_MAX_OUTPUT_TOKENS = 1200
DEFAULT_SYSTEM_PROMPT_PATH = PROMPTS_DIR / "system_prompt.md"
DEFAULT_USER_PROMPT_PATH = PROMPTS_DIR / "user_prompt.md"


def load_local_env() -> None:
    if load_dotenv is not None:
        load_dotenv(ROOT_DIR / ".env", override=True)


def env_text(name: str, default: str = "") -> str:
    return os.environ.get(name, "").strip() or default


def env_int(name: str, default: int) -> int:
    value = os.environ.get(name, "").strip()
    if not value:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise SystemExit(f"Invalid integer value for {name}: {value!r}") from exc


def env_optional_float(name: str) -> float | None:
    value = os.environ.get(name, "").strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise SystemExit(f"Invalid float value for {name}: {value!r}") from exc


def resolve_public_dataset_path(explicit: str | Path | None = None) -> Path:
    if explicit is not None:
        return Path(explicit).expanduser().resolve()
    env_path = env_text("CITEBENCH_PUBLIC_DATASET")
    if env_path:
        return Path(env_path).expanduser().resolve()
    return (ROOT_DIR / "data" / PUBLIC_JSON_NAME).resolve()


def default_output_dir() -> Path:
    return ROOT_DIR / "outputs"


def describe_defaults() -> dict[str, str | int | bool | None]:
    public_dataset = resolve_public_dataset_path()
    return {
        "root_dir": str(ROOT_DIR),
        "public_dataset_path": str(public_dataset),
        "public_dataset_exists": public_dataset.exists(),
        "default_model": env_text("OPENAI_DEFAULT_MODEL", DEFAULT_MODEL),
        "default_reasoning_effort": env_text(
            "OPENAI_REASONING_EFFORT", DEFAULT_REASONING_EFFORT
        ),
        "default_concurrency": env_int("OPENAI_CONCURRENCY", DEFAULT_CONCURRENCY),
        "default_max_output_tokens": env_int(
            "OPENAI_MAX_OUTPUT_TOKENS", DEFAULT_MAX_OUTPUT_TOKENS
        ),
        "default_system_prompt_path": str(DEFAULT_SYSTEM_PROMPT_PATH),
        "default_user_prompt_path": str(DEFAULT_USER_PROMPT_PATH),
    }


def load_prompt_text(path: str | Path, *, fallback: str | None = None) -> str:
    prompt_path = Path(path).expanduser().resolve()
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8").strip()
    if fallback is not None:
        return fallback.strip()
    raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
