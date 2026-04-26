# X (Twitter) Search MCP サーバー

このリポジトリは、xAI の [Responses API](https://docs.x.ai/developers/tools/overview) と
[x_search サーバーサイドツール](https://docs.x.ai/developers/tools/x-search)を使って、
MCP クライアントから X（Twitter）をリアルタイム検索できる MCP サーバーです。

> English README: [README.md](./README.md)

## 対応トランスポート

- `stdio`（ローカルプロセス）
- `Streamable HTTP`（Remote MCP）

## 主な機能

| ツール | 説明 |
|---|---|
| `x_search_posts` | キーワード・ハッシュタグ・話題で X 投稿を検索 |
| `x_get_user_posts` | 指定ユーザーの最近の投稿を取得 |
| `x_get_trending` | 現在のトレンドを取得 |

## 前提条件

- Python 3.10+
- xAI API キー（https://console.x.ai/ で取得）

## セットアップ

```bash
git clone https://github.com/toocheap/x-search-mcp.git
cd x-search-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## サーバー起動

### 1) stdio モード

```bash
XAI_API_KEY="xai-..." \
python x_search_mcp.py --transport stdio
```

デフォルトトランスポートは `stdio` なので、環境変数のみでも起動できます。

```bash
MCP_TRANSPORT=stdio XAI_API_KEY="xai-..." python x_search_mcp.py
```

### 2) Streamable HTTP モード（Remote MCP）

HTTP モードでは以下を公開します。

- MCP エンドポイント: `/mcp`
- ヘルスチェック: `/health`

```bash
XAI_API_KEY="xai-..." \
MCP_AUTH_TOKEN="change-me" \
MCP_CORS_ORIGINS="https://your-client.example,https://another.example" \
python x_search_mcp.py --transport http --host 0.0.0.0 --port 8000
```

主な HTTP 関連環境変数:

- `MCP_TRANSPORT=http`
- `MCP_HTTP_HOST`（既定: `127.0.0.1`）
- `MCP_HTTP_PORT`（既定: `8000`）
- `MCP_AUTH_TOKEN`（**HTTP モードでは必須**）
- `MCP_CORS_ORIGINS`（カンマ区切り。既定: `*`）

## MCP クライアント設定例

### stdio 例（Claude Desktop など）

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

### Remote MCP 例（Streamable HTTP）

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

ヘルスチェック例:

```bash
curl -i https://mcp.example.com/health
```

## モデル対応

`x_search` サーバーサイドツールは **grok-4 系モデル**で利用できます。

- `grok-4.20-reasoning`（既定）
- `grok-4-1-fast`
- `grok-4-1-fast-reasoning`

モデルを変更する場合は `XAI_MODEL` 環境変数を設定してください。

## ライセンス

MIT License。

このリポジトリは [toocheap/x-search-mcp](https://github.com/toocheap/x-search-mcp) の fork です。
本 fork では Remote MCP / Streamable HTTP 対応などを追加しています。

詳細は [LICENSE](./LICENSE) を参照してください。
