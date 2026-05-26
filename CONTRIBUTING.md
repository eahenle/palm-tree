# Contributing

Thanks for contributing to **palm-tree**.

## Local development checks

Run the following checks before opening a pull request:

```bash
black --check .
pytest -q
ruff check .
mypy .
```

Install required tooling first (the root `requirements.txt` does **not** include
`black`, `ruff`, or `mypy`):

```bash
pip install -r requirements.txt black ruff mypy
```

## Commit message format

Use `type: summary`, for example:

- `feat: add nightly review notifier`
- `fix: handle missing github token`
- `docs: clarify publishing setup`

## Pull request checklist

- Include a **Summary** section
- Include a **Testing** section with command results
- Keep changes focused and small when possible
