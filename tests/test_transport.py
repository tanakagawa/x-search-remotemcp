"""Tests for transport selection and HTTP middleware helpers."""

from __future__ import annotations

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from x_search_mcp import BearerAuthMiddleware, _parse_origins


async def ok(_: object) -> JSONResponse:
    return JSONResponse({"ok": True})


def _client_with_auth(token: str = "secret") -> TestClient:
    app = Starlette(routes=[Route("/mcp", ok, methods=["GET"]), Route("/health", ok)])
    app.add_middleware(BearerAuthMiddleware, token=token)
    return TestClient(app)


def test_parse_origins_csv() -> None:
    assert _parse_origins("https://a.example, https://b.example") == [
        "https://a.example",
        "https://b.example",
    ]


def test_parse_origins_empty_defaults_to_wildcard() -> None:
    assert _parse_origins("") == ["*"]


def test_auth_middleware_rejects_missing_token() -> None:
    with _client_with_auth() as client:
        resp = client.get("/mcp")
    assert resp.status_code == 401


def test_auth_middleware_accepts_valid_token() -> None:
    with _client_with_auth() as client:
        resp = client.get("/mcp", headers={"Authorization": "Bearer secret"})
    assert resp.status_code == 200


def test_auth_middleware_skips_health() -> None:
    with _client_with_auth() as client:
        resp = client.get("/health")
    assert resp.status_code == 200
