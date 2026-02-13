# Contributing

Thanks for contributing to Sentinel Stream.

## Development setup
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

pip install -e ".[dev]"
ruff check .
pytest
```

## Project structure
- `sentinel_stream/collector/` – event collectors
- `sentinel_stream/pipeline/` – rule evaluation + orchestration
- `sentinel_stream/storage/` – persistence backends
- `sentinel_stream/api/` – optional FastAPI read API

## Guidelines
- Keep collectors **local-first** and safe by default.
- Prefer small, typed modules with clear interfaces.
- Add/adjust tests for behavior changes.
- Avoid committing secrets or sensitive logs.

## Pull requests
- Include a clear description and rationale.
- Keep changes cohesive.
- Ensure CI passes.
