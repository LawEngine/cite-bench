from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(slots=True)
class BenchmarkCase:
    id: str
    citation: str
    quote: str


def load_public_dataset(path: Path) -> list[BenchmarkCase]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("cases") or payload.get("rows") or payload.get("items")
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"No benchmark rows found in {path}")

    cases: list[BenchmarkCase] = []
    for index, row in enumerate(rows):
        try:
            cases.append(
                BenchmarkCase(
                    id=str(row["id"]).strip(),
                    citation=str(row["citation"]).strip(),
                    quote=str(row["quote"]).strip(),
                )
            )
        except KeyError as exc:
            raise ValueError(f"Row {index} in {path} is missing {exc.args[0]!r}") from exc
    return cases


def write_submission_csv(rows: Iterable[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "predicted_status"])
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "id": str(row["id"]),
                    "predicted_status": str(row.get("predicted_status", "") or ""),
                }
            )


def write_audit_jsonl(rows: Iterable[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def cases_to_dicts(cases: Iterable[BenchmarkCase]) -> list[dict[str, str]]:
    return [asdict(case) for case in cases]
