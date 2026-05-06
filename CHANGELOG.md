# Changelog

## [0.1.0] - 2026-05-07

### Added
- `promptvc init` — initialize a `.promptvc/` store
- `promptvc add` — stage prompt content for commit
- `promptvc commit` — commit staged prompt with a message
- `promptvc log` — view version history
- `promptvc show` — display prompt at a specific version
- `promptvc diff` — unified diff between two versions
- `promptvc rollback` — non-destructive rollback to a previous version
- `promptvc list` — list all tracked prompts
- `promptvc env` — view and set the active environment
- `promptvc export` — export version history to JSON/YAML
- `promptvc tag` — tag a version with a label
- `promptvc search` — full-text search across all prompt content
- SQLite-backed local storage with FTS5 search
- Token counting via tiktoken (falls back to word estimate)
- Rich terminal UI with colored diffs and tables
