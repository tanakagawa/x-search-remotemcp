# X Search MCP Server

MCP server for real-time X (Twitter) search using xAI Responses API and the `x_search` server-side tool.

## Runtime and Entry Point

- Required environment variable: `XAI_API_KEY` (https://console.x.ai/)
- Main entry point: `x_search_mcp.py`
- Process start: `main()`

## Transport Specification (Current)

The project supports two MCP transports:

1. `stdio`
   - Local process integration for desktop MCP clients.
2. `Streamable HTTP`
   - Remote MCP deployment with bearer authentication and CORS.
   - MCP endpoint: `/mcp`
   - Health endpoint: `/health`

HTTP mode requirements:

- `MCP_AUTH_TOKEN` is required.
- CORS origins are controlled by `MCP_CORS_ORIGINS` (comma-separated, default `*`).
- Host/port can be set with CLI args or `MCP_HTTP_HOST` / `MCP_HTTP_PORT`.

## R Specification (Responses API Contract)

The server integrates with xAI **Responses API** (`/v1/responses`) using:

- Model constant: `XAI_MODEL` (default: `grok-4-1-fast`)
- Tool declaration: `{ "type": "x_search" }`
- Request body fields:
  - `model`
  - `input` (user prompt)
  - `tools` (includes x_search configuration)

`_call_responses_api()` handles the API call and extracts message text from `output`.
If no plain message text is found, raw JSON is returned as formatted text.

## Architecture

### stdio mode

```
MCP Client <-> MCP Server (stdio) <-> xAI Responses API (/v1/responses)
                                              |
                                         x_search tool
                                        (server-side)
                                              |
                                         X (Twitter) data
```

### HTTP mode

```
Remote MCP Client <-> HTTPS /mcp (Bearer + CORS) <-> MCP Server <-> xAI Responses API
                       \-> /health
```

## Tools (Read-only)

| Tool | Input Model | Description |
|---|---|---|
| `x_search_posts` | `XSearchPostsInput` | Search posts by keyword, hashtag, or topic |
| `x_get_user_posts` | `XGetUserPostsInput` | Fetch recent posts from a specific user |
| `x_get_trending` | `XTrendingInput` | Fetch trending topics |

### Common Parameters

- `response_format`: `"markdown"` (default) or `"json"`
- `max_results`: `1` to `30` (default `10`, where applicable)
- `from_date` / `to_date`: `YYYY-MM-DD` date filters (where applicable)

## Internal Helpers

| Function | Purpose |
|---|---|
| `_get_api_key()` | Load `XAI_API_KEY`; raises `RuntimeError` if missing |
| `_call_responses_api()` | Call xAI `/v1/responses` |
| `_build_x_search_config()` | Build `x_search` tool config dict |
| `_handle_api_error()` | Normalize API and timeout errors into JSON text |
| `create_mcp_server()` | Register tools and create MCP server instance |

## Dependencies

Core dependencies currently declared in `requirements.txt`:

- `mcp>=1.26.0`
- `httpx>=0.28.0`
- `pydantic>=2.12.0`

Runtime in HTTP mode additionally relies on `uvicorn` and Starlette middleware available in the environment.

## Coding Conventions

- Keep comments and docs in English.
- Use explicit type hints for all functions.
- Use Pydantic `BaseModel` inputs with `ConfigDict(extra="forbid")`.
- Implement tools as `async def`.
- Use `@mcp.tool(name=..., annotations={...})` for MCP tool registration.
- Provide actionable user-facing error messages.
- Use `httpx.AsyncClient` with timeout for external HTTP calls.
- Read environment variables dynamically inside functions for testability.
- Route API errors through `_handle_api_error()` for consistent output.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# stdio mode
XAI_API_KEY="xai-xxx" python3 x_search_mcp.py --transport stdio

# HTTP mode
XAI_API_KEY="xai-xxx" MCP_AUTH_TOKEN="change-me" python3 x_search_mcp.py --transport http
```

## Testing and Quality

Tests use `pytest` and `pytest-asyncio`.

### Test Strategy

1. Validate normal and error paths for all tools and helpers.
2. Cover invalid input, API errors (401/429/5xx), timeouts, and missing env vars.
3. Keep test isolation using `monkeypatch` for environment/global state.
4. Validate Pydantic model constraints, required fields, and `extra="forbid"` behavior.

### Unit vs Integration

- Unit tests: `tests/`
- Integration tests (live API): `tests/integration/` with `@pytest.mark.integration`

### Commands

```bash
pip install pytest pytest-asyncio pytest-cov pytest-timeout
export PYTHONPATH=$PYTHONPATH:.

# Unit tests
pytest tests/ --ignore=tests/integration/

# Unit tests + coverage
pytest tests/ --ignore=tests/integration/ --cov=. --cov-report=term-missing

# Integration tests (requires real API key)
XAI_API_KEY="xai-xxx" pytest tests/integration/ -m integration --timeout=30

# Full test suite
XAI_API_KEY="xai-xxx" pytest tests/ --timeout=30
```
