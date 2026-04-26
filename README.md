# X (Twitter) Search MCP Server

An MCP server that enables real-time X (Twitter) search from MCP clients using xAI's [Responses API](https://docs.x.ai/developers/tools/overview) and the [x_search server-side tool](https://docs.x.ai/developers/tools/x-search).

[日本語版 README](./README.ja.md)

This server supports **dual transport modes**:

- `stdio` (local process mode)
- `Streamable HTTP` (remote MCP mode)

## Features

| Tool | Description |
|---|---|
| `x_search_posts` | Search X posts by keyword, hashtag, or topic |
| `x_get_user_posts` | Fetch recent posts from a specific user |
| `x_get_trending` | Fetch currently trending topics |

## Prerequisites

- Python 3.10+
- xAI API key (from https://console.x.ai/)

## Setup

```bash
git clone https://github.com/tanakagawa/x-search-remotemcp.git
cd x-search-remotemcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the Server

### 1) stdio transport

```bash
XAI_API_KEY="xai-..." \
python x_search_mcp.py --transport stdio
```

You can also use environment variables only (default transport is `stdio`):

```bash
MCP_TRANSPORT=stdio XAI_API_KEY="xai-..." python x_search_mcp.py
```

### 2) Streamable HTTP transport (remote MCP)

In HTTP mode, the server exposes:

- MCP endpoint: `/mcp`
- Health endpoint: `/health`

```bash
XAI_API_KEY="xai-..." \
MCP_AUTH_TOKEN="change-me" \
MCP_CORS_ORIGINS="https://your-client.example,https://another.example" \
python x_search_mcp.py --transport http --host 0.0.0.0 --port 8000
```

Main HTTP-related environment variables:

- `MCP_TRANSPORT=http`
- `MCP_HTTP_HOST` (default: `127.0.0.1`)
- `MCP_HTTP_PORT` (default: `8000`)
- `MCP_AUTH_TOKEN` (**required in HTTP mode**)
- `MCP_CORS_ORIGINS` (comma-separated, default: `*`)

## MCP Client Configuration Examples

### stdio example (Claude Desktop, etc.)

```json
{
  "mcpServers": {
    "x_search": {
      "command": "/absolute/path/to/x-search-mcp/.venv/bin/python3",
      "args": [
        "/absolute/path/to/x-search-mcp/x_search_mcp.py",
        "--transport",
        "stdio"
      ],
      "env": {
        "XAI_API_KEY": "xai-xxxxxxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

### Remote MCP example (Streamable HTTP)

If your MCP client supports remote MCP, configure the URL and headers like this (field names may differ by client implementation):

```json
{
  "mcpServers": {
    "x_search_remote": {
      "transport": "streamable-http",
      "url": "https://mcp.example.com/mcp",
      "headers": {
        "Authorization": "Bearer change-me"
      }
    }
  }
}
```

Health check example:

```bash
curl -i https://mcp.example.com/health
```

## Example Prompts

- "Search for the latest AI posts on X."
- "Show recent posts by @elonmusk."
- "What is trending in Japan right now?"
- "Search #cybersecurity posts in Japanese."

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

## Model Support

The `x_search` server-side tool is available on **grok-4 family models**.

| Model | Notes |
|---|---|
| `grok-4.20-reasoning` | Latest flagship reasoning model (**default**) |
| `grok-4-1-fast` | Fast and widely compatible |
| `grok-4-1-fast-reasoning` | Higher reasoning quality |

To change the model, set the `XAI_MODEL` environment variable (default: `grok-4.20-reasoning`).

## License

MIT License.

This repository is a fork of [toocheap/x-search-mcp](https://github.com/toocheap/x-search-mcp),
which states `MIT` in its README.

This fork adds Remote MCP / Streamable HTTP support and related product updates.

Copyright (c) 2026 tanakagawa and contributors.

See [LICENSE](./LICENSE) for details.
