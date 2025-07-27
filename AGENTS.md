# AGENT GUIDELINES

This repository does not yet have detailed contributing instructions. The
following guidelines serve as an initial template for agents making
contributions.

## Commit messages
- Use short, descriptive commit messages in the form `type: summary`. Examples
  include `feat: add new tool`, `fix: correct typo`, or `docs: update README`.

## Code style
- Ensure all Python files are formatted with **black** using `black .` or
  `black --check .`.

## Testing
- Run the unit tests with `pytest -q` and ensure they pass before committing.

## Pull request message
- Summarize the changes in a **Summary** section.
- Include test results in a **Testing** section. If tests cannot be run, state
  the reason.
