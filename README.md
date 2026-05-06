# promptvc — Git for your prompts

> Version, diff, rollback, and ship prompts like code.

[![CI](https://github.com/ANIMESHIOLOGY/prompt-version-control/actions/workflows/ci.yml/badge.svg)](https://github.com/ANIMESHIOLOGY/prompt-version-control/actions)
[![PyPI](https://img.shields.io/pypi/v/promptvc)](https://pypi.org/project/promptvc/)
[![Python](https://img.shields.io/pypi/pyversions/promptvc)](https://pypi.org/project/promptvc/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Why?

LLM engineers change prompts constantly but track them nowhere. There is no `git log` for prompts, no `git diff` between prompt versions, no `git checkout` to roll back a bad change. **promptvc** fixes this — zero infra, just a local SQLite file.

## Install

```bash
pip install promptvc
```

For YAML export support:

```bash
pip install "promptvc[yaml]"
```

## Quick Start

```bash
# Initialize in your project directory
promptvc init

# Stage a prompt (opens $EDITOR)
promptvc add summarizer

# Commit it
promptvc commit summarizer -m "initial version"

# Edit and commit again
promptvc add summarizer
promptvc commit summarizer -m "made it more concise"

# See what changed
promptvc diff summarizer

# Full history
promptvc log summarizer

# Show a specific version
promptvc show summarizer --version 1

# Roll back (non-destructive — creates a new version)
promptvc rollback summarizer --version 1

# Tag a stable version
promptvc tag summarizer 1 stable

# Search across all prompts
promptvc search "summarization assistant"

# Export to JSON
promptvc export summarizer --output summarizer.json
```

## Commands

| Command | Description |
|---|---|
| `promptvc init` | Initialize `.promptvc/` store in current directory |
| `promptvc add <name>` | Stage a prompt (editor / `--file` / stdin) |
| `promptvc commit <name> -m "msg"` | Commit staged prompt |
| `promptvc log <name>` | Show version history |
| `promptvc show <name>` | Display prompt content at a version |
| `promptvc diff <name>` | Unified diff between versions |
| `promptvc rollback <name> --version N` | Non-destructive rollback |
| `promptvc list` | List all tracked prompts |
| `promptvc env [set dev\|staging\|prod]` | View or set active environment |
| `promptvc export <name>` | Export history to JSON/YAML |
| `promptvc tag <name> <version> <label>` | Tag a version |
| `promptvc search <query>` | Full-text search |

## Features

- **Zero infra** — local SQLite (`.promptvc/store.db`), nothing to deploy
- **Works alongside Git** — version your prompts alongside your code
- **Multi-environment** — `dev`, `staging`, `prod` support per version
- **Token counting** — via tiktoken (falls back to word estimate)
- **Full-text search** — SQLite FTS5 across all content and commit messages
- **Non-destructive** — rollback creates a new version, history is never deleted
- **Rich UI** — colored diffs, tables, syntax highlighting

## Roadmap

- [ ] Remote registry (`promptvc push` / `promptvc pull`)
- [ ] GitHub Actions integration
- [ ] VS Code extension
- [ ] Team sharing via shared SQLite on S3 / network drive
