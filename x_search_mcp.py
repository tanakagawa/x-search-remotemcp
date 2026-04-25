#!/usr/bin/env python3
"""X Search MCP server entrypoint supporting stdio and streamable HTTP."""

from __future__ import annotations

import argparse
import os

import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from x_search_common import (  # re-export for tests/backward compatibility
    DEFAULT_TIMEOUT,
    MAX_RESULTS_DEFAULT,
    ResponseFormat,
    XGetUserPostsInput,
    XSearchPostsInput,
    XTrendingInput,
    _build_x_search_config,
    _call_responses_api,
    _get_api_key,
    _handle_api_error,
    create_mcp_server,
    x_get_trending,
    x_get_user_posts,
    x_search_posts,
)


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Simple bearer token auth for HTTP MCP endpoint."""

    def __init__(self, app, token: str) -> None:  # noqa: ANN001
        super().__init__(app)
        self._token = token

    async def dispatch(self, request: Request, call_next):  # noqa: ANN001
        if request.method == "OPTIONS" or request.url.path == "/health":
            return await call_next(request)

        expected = f"Bearer {self._token}"
        if request.headers.get("authorization") != expected:
            return JSONResponse(
                {"error": "Unauthorized"},
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="X Search MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default=os.environ.get("MCP_TRANSPORT", "stdio"),
        help="Transport mode: stdio or http (default: env MCP_TRANSPORT or stdio)",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_HTTP_HOST", "127.0.0.1"),
        help="HTTP host (default: env MCP_HTTP_HOST or 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("MCP_HTTP_PORT", "8000")),
        help="HTTP port (default: env MCP_HTTP_PORT or 8000)",
    )
    parser.add_argument(
        "--auth-token",
        default=os.environ.get("MCP_AUTH_TOKEN", ""),
        help="Bearer auth token for HTTP mode (default: env MCP_AUTH_TOKEN)",
    )
    parser.add_argument(
        "--cors-origins",
        default=os.environ.get("MCP_CORS_ORIGINS", "*"),
        help="Comma-separated CORS origins for HTTP mode (default: *)",
    )
    return parser.parse_args()


def _parse_origins(csv_origins: str) -> list[str]:
    origins = [origin.strip() for origin in csv_origins.split(",") if origin.strip()]
    return origins or ["*"]


def _run_http(host: str, port: int, auth_token: str, cors_origins: str) -> None:
    if not auth_token:
        raise RuntimeError(
            "HTTP mode requires bearer auth. Set --auth-token or MCP_AUTH_TOKEN."
        )

    mcp = create_mcp_server(host=host, port=port, streamable_http_path="/mcp")
    app = mcp.streamable_http_app()

    @app.route("/health", methods=["GET"])
    async def health(_: Request) -> Response:
        return JSONResponse({"status": "ok"})

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_parse_origins(cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    app.add_middleware(BearerAuthMiddleware, token=auth_token)

    uvicorn.run(app, host=host, port=port)


def main() -> None:
    args = _parse_args()

    if args.transport == "stdio":
        create_mcp_server().run(transport="stdio")
        return

    _run_http(
        host=args.host,
        port=args.port,
        auth_token=args.auth_token,
        cors_origins=args.cors_origins,
    )


if __name__ == "__main__":
    main()
