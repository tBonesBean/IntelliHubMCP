import argparse
import asyncio
import json

import websockets


async def main(host: str, port: int, path: str):
    # Normalize path to start with a slash
    path = path if path.startswith("/") else f"/{path}"
    uri = f"ws://{host}:{port}{path}"
    async with websockets.connect(uri, subprotocols=["mcp"]) as ws:
        init = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {"name": "endpoint-check", "version": "0.0.1"},
                "capabilities": {"experimental": {}},
            },
        }
        await ws.send(json.dumps(init))
        print("init ->", await ws.recv())

        await ws.send(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}))
        print("list_tools ->", await ws.recv())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check MCP endpoint health")
    parser.add_argument("--host", default="127.0.0.1", help="Host of the MCP server")
    parser.add_argument("--port", type=int, default=8000, help="Port of the MCP server")
    parser.add_argument("--path", default="/mcp", help="WebSocket path (default: /mcp)")
    args = parser.parse_args()

    try:
        asyncio.run(main(args.host, args.port, args.path))
    except KeyboardInterrupt:
        pass
    except Exception as exc:  # pragma: no cover - runtime guard
        raise SystemExit(f"Endpoint check failed: {exc}")
