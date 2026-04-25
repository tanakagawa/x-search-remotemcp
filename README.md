# X (Twitter) Search MCP Server

xAI の [Responses API](https://docs.x.ai/developers/tools/overview) + [x_search サーバーサイドツール](https://docs.x.ai/developers/tools/x-search)を利用して、MCP 対応クライアントから X (Twitter) の投稿をリアルタイム検索できる MCP サーバーです。

このサーバーは **dual transport 対応**です。

- `stdio`（ローカル起動）
- `Streamable HTTP`（remote MCP として公開）

## 機能

| ツール名 | 機能 |
|---|---|
| `x_search_posts` | キーワード・ハッシュタグ・トピックで X の投稿を検索 |
| `x_get_user_posts` | 特定ユーザーの最近の投稿を取得（`allowed_x_handles` で絞り込み） |
| `x_get_trending` | トレンドトピックを取得 |

## セットアップ

### 前提条件

- Python 3.10 以上
- xAI API キー（ https://console.x.ai/ から取得）

### 1. リポジトリのクローンと仮想環境の作成

```bash
git clone https://github.com/toocheap/x-search-mcp.git
cd x-search-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 起動方法

### 1) stdio transport（従来）

```bash
XAI_API_KEY="xai-..." \
python x_search_mcp.py --transport stdio
```

環境変数だけでも指定できます（デフォルトは stdio）。

```bash
MCP_TRANSPORT=stdio XAI_API_KEY="xai-..." python x_search_mcp.py
```

### 2) Streamable HTTP transport（remote MCP）

`/mcp` エンドポイントで MCP を提供します。さらに `/health` ヘルスチェックを提供します。

```bash
XAI_API_KEY="xai-..." \
MCP_AUTH_TOKEN="change-me" \
MCP_CORS_ORIGINS="https://your-client.example,https://another.example" \
python x_search_mcp.py --transport http --host 0.0.0.0 --port 8000
```

HTTP モード時の主な環境変数:

- `MCP_TRANSPORT=http`
- `MCP_HTTP_HOST`（デフォルト `127.0.0.1`）
- `MCP_HTTP_PORT`（デフォルト `8000`）
- `MCP_AUTH_TOKEN`（必須）
- `MCP_CORS_ORIGINS`（カンマ区切り、デフォルト `*`）

## MCP クライアント設定例

### stdio 設定例（Claude Desktop 等）

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

### remote MCP 設定例（Streamable HTTP）

クライアント側が remote MCP をサポートしている場合、以下のように URL とヘッダーを指定します（キー名はクライアント実装に合わせて調整してください）。

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

## 使用例

- 「AIに関する最新のツイートを検索して」
- 「@elonmusk の最近の投稿を見せて」
- 「日本でのトレンドを教えて」
- 「#cybersecurity のツイートを日本語で検索」

## アーキテクチャ

### stdio モード

```
MCP Client <-> MCP Server (stdio) <-> xAI Responses API (/v1/responses)
                                            |
                                       x_search tool
                                      (server-side)
                                            |
                                       X (Twitter) data
```

### HTTP モード

```
Remote MCP Client <-> HTTPS /mcp (Bearer + CORS) <-> MCP Server <-> xAI Responses API
                       \-> /health
```

## モデル

`x_search` サーバーサイドツールは **grok-4 系モデルのみ**で利用可能です。

| モデル | 特徴 |
|---|---|
| `grok-4-1-fast` | ツール呼び出し最適化・高速（**デフォルト**） |
| `grok-4-1-fast-reasoning` | 推論付き・より高精度 |

モデルを変更する場合は `x_search_common.py` 内の `XAI_MODEL` 定数を編集してください。

## ライセンス

MIT
