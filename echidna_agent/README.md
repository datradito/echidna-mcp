# Echidna Agent MCP Server

Python-based MCP server for Echidna smart contract auditing agents.

## Features

- **Issue Triage Agent**: Classifies failure logs.
- **Fuzzer Optimization Agent**: Suggests fuzzing parameters.
- **Report Summarizer Agent**: Generates audit reports.
- **Fix Suggestion Agent**: Proposes code patches.
- **Trend Analysis Agent**: Analyzes historical audit data.

## Installation

1. Install `uv`:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Install dependencies:
   ```bash
   cd echidna_agent
   uv sync
   ```

3. Configure environment:
   Copy `.env.example` to `.env` and set your API keys and DB URL.
   ```bash
   cp .env.example .env
   ```

4. Initialize Database:
   ```bash
   uv run python -m echidna_agent.db
   ```

## Usage

Run the MCP server:
```bash
uv run python -m echidna_agent.server
```

## Testing

Run tests:
```bash
uv run pytest ../tests/echidna_agent
```
