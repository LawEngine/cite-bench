# cite-bench v1

`cite-bench` is a public benchmark for legal citation verification.

Given a citation and a quoted passage, a model must classify the pair as one
of four labels:

- `VERIFIED` — the quote belongs in the cited provision
- `NOT_FOUND` — the citation is real but the quote is fabricated or altered
- `MISATTRIBUTED` — the quote is real legal text but from a different provision
- `CITATION_UNRESOLVED` — the citation itself is malformed or nonexistent

This public repo ships:

- a public benchmark input pack
- a blank submission template
- sample prompts
- a public runner that produces `id,predicted_status` CSV submissions

This public repo does not ship:

- private grading keys
- hidden eval or holdout packs
- local scoring code
- backend upload or grading services

## Quick Start

```bash
git clone https://github.com/LawEngine/cite-bench.git
cd cite-bench
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Add your `OPENAI_API_KEY` to `.env`.

## Repo Layout

```text
cite-bench/
├── citebench/
├── data/
├── prompts/
├── results/
└── scripts/
```

Key tracked files:

- `data/cite-bench-v1.json`
- `data/submission_template.csv`
- `prompts/system_prompt.md`
- `prompts/user_prompt.md`
- `scripts/run_openai.py`

## Dataset Contract

The public dataset rows contain only:

- `id`
- `citation`
- `quote`

The public pack intentionally does not include private grading metadata such as
`expected_status` or internal source hints.

## Run The Public Benchmark

Smoke test:

```bash
.venv/bin/python scripts/run_openai.py \
  --limit 5 \
  --output outputs/submissions/probe_5.csv \
  --audit outputs/audit/probe_5.jsonl
```

Full public pack:

```bash
.venv/bin/python scripts/run_openai.py \
  --output outputs/submissions/citebench_v1.csv \
  --audit outputs/audit/citebench_v1.jsonl
```

You can also override model settings:

```bash
.venv/bin/python scripts/run_openai.py \
  --model gpt-5.4-mini \
  --reasoning-effort high \
  --concurrency 20 \
  --max-output-tokens 1600
```

## Output Contract

Submission CSVs use this schema:

```csv
id,predicted_status
```

`predicted_status` must be exactly one of:

- `VERIFIED`
- `NOT_FOUND`
- `MISATTRIBUTED`
- `CITATION_UNRESOLVED`

## Public Prompt Baseline

The tracked prompt pair is:

- `prompts/system_prompt.md`
- `prompts/user_prompt.md`

These are public baseline prompts, not private max-performance prompts.

## Scoring Boundary

Official grading is intentionally not included in this public repo.

The public repo is for:

- downloading the public pack
- running a model
- generating a valid submission CSV

Private grading keys and backend upload/scoring logic live outside this repo.

## Licensing

Software source code in this repository is licensed under `Apache-2.0`. See
`LICENSE`.

The benchmark dataset, prompt files, and benchmark-facing documentation are
licensed under `CC BY 4.0`. See `DATA_LICENSE.md`.

## Development Notes

Private operator notes and local setup docs are intentionally kept out of
tracked git paths in this repo.
