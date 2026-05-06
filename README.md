# promptvc: Git for your prompts

> Version, diff, rollback, and ship prompts like code.

[![CI](https://github.com/ANIMESHIOLOGY/prompt-version-control/actions/workflows/ci.yml/badge.svg)](https://github.com/ANIMESHIOLOGY/prompt-version-control/actions)
[![PyPI](https://img.shields.io/pypi/v/promptvc)](https://pypi.org/project/promptvc/)
[![Python](https://img.shields.io/pypi/pyversions/promptvc)](https://pypi.org/project/promptvc/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Why?

LLM engineers change prompts constantly but track them nowhere. There is no `git log` for prompts, no `git diff` between versions, no `git checkout` to roll back a bad change. **promptvc** fixes this with zero infra and just a local SQLite file.

## Install

```bash
pip install promptvc
```

Optional extras:

```bash
pip install "promptvc[yaml]"   # YAML export support
pip install "promptvc[s3]"     # S3 remote sync
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

# Roll back (non-destructive, creates a new version)
promptvc rollback summarizer --version 1

# Tag a stable version
promptvc tag summarizer 1 stable

# Search across all prompts
promptvc search "summarization assistant"

# Export to JSON
promptvc export summarizer --output summarizer.json
```

## Team Sharing

Push your prompt store to a private GitHub Gist and share the ID with teammates:

```bash
# First push (creates the Gist, saves ID to config)
promptvc push --gist --token <your-github-pat>

# Teammates pull and merge into their local store
promptvc pull <gist-id>

# Subsequent pushes update the same Gist automatically
promptvc push --gist
```

Or use S3:

```bash
promptvc push --bucket my-team-bucket --key prompts/store.json
promptvc pull s3://my-team-bucket/prompts/store.json
```

Pull is always safe: it merges by content hash, so no duplicate versions are created.

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
| `promptvc push` | Push store to GitHub Gist or S3 |
| `promptvc pull <remote>` | Pull and merge from a remote |

## Features

- **Zero infra**: local SQLite (`.promptvc/store.db`), nothing to deploy
- **Works alongside Git**: version your prompts next to your code
- **Multi-environment**: `dev`, `staging`, `prod` support per version
- **Token counting**: via tiktoken, falls back to word estimate
- **Full-text search**: SQLite FTS5 across all content and commit messages
- **Non-destructive**: rollback and pull always create new versions, history is never deleted
- **Team sharing**: push/pull via GitHub Gist or S3
- **Rich UI**: colored diffs, tables, syntax highlighting

## Roadmap

- [x] Remote sync via GitHub Gist
- [x] Remote sync via S3
- [ ] GitHub Actions integration
- [ ] VS Code extension
