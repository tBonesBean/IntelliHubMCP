import asyncio
import json
import os
import argparse
from mcp.server import Server
from mcp import types
from mcp.server.websocket import websocket_server
from starlette.applications import Starlette
from starlette.routing import WebSocketRoute, Route
from starlette.responses import JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware



import tool as tool_impl

# Load manifest
MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "manifest.json")
with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
    MANIFEST = json.load(f)

# Create MCP server
mcp = Server(
    name=MANIFEST["name"],
    version=MANIFEST["version"],
)

# ---- Tool implementations ----


async def list_files():
    return await asyncio.to_thread(tool_impl.list_files)


async def read_file(path: str):
    return await asyncio.to_thread(tool_impl.read_file, path)


async def search(query: str):
    return await asyncio.to_thread(tool_impl.search, query)


async def get_schema(name: str):
    return await asyncio.to_thread(tool_impl.get_schema, name)


async def get_module_purpose(name: str):
    return await asyncio.to_thread(tool_impl.get_module_purpose, name)


async def diagnose():
    return await asyncio.to_thread(tool_impl.diagnose)


# Dictionary to map tool names to functions
TOOL_IMPLEMENTATIONS = {
    "list_files": list_files,
    "read_file": read_file,
    "search": search,
    "get_schema": get_schema,
    "get_module_purpose": get_module_purpose,
    "diagnose": diagnose,
}

TOOLS = [
    types.Tool(
        name="list_files",
        description="Returns a list of all files within the ai_context directory.",
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
    types.Tool(
        name="read_file",
        description="Reads and returns the contents of a Markdown file.",
        inputSchema={
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    ),
    types.Tool(
        name="search",
        description="Searches across all Markdown files and returns matching snippets.",
        inputSchema={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    ),
    types.Tool(
        name="get_schema",
        description="Returns the contents of a schema file from the schemas directory.",
        inputSchema={
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    ),
    types.Tool(
        name="get_module_purpose",
        description="Returns the contents of a module purpose file.",
        inputSchema={
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    ),
    types.Tool(
        name="diagnose",
        description="Performs a full health check of the IntelliHub knowledge capsule.",
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
]


@mcp.list_tools()
async def list_tools_handler():
    return TOOLS


@mcp.call_tool()
async def call_tool_handler(name: str, arguments: dict):
    tool_func = TOOL_IMPLEMENTATIONS.get(name)
    if not tool_func:
        raise ValueError(f"Tool '{name}' not found.")

    result = await tool_func(**arguments)

    if isinstance(result, str):
        return [types.TextContent(type="text", text=result)]
    else:
        # For list_files, search, diagnose, the result is JSON-serializable.
        # This will be returned as structuredContent, and also as a JSON string in content.
        return {"result": result}


async def mcp_endpoint(websocket):
    """MCP WebSocket endpoint."""
    async with websocket_server(websocket.scope, websocket.receive, websocket.send) as (
        read_stream,
        write_stream,
    ):
        await mcp.run(
            read_stream,
            write_stream,
            initialization_options=mcp.create_initialization_options(),
        )


async def health_check(request):
    """Health check endpoint."""
    return JSONResponse({"status": "ok"})


routes = [
    WebSocketRoute("/mcp", mcp_endpoint),
    Route("/health", health_check),
]

# Enables CORS
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
]

app = Starlette(routes=routes, middleware=middleware)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run IntelliHub MCP server with uvicorn")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    parser.add_argument("--reload", action="store_true", help="Enable autoreload")
    args = parser.parse_args()

    try:
        import uvicorn
    except ImportError:  # pragma: no cover - import-time guard
        raise SystemExit("uvicorn is required: pip install uvicorn")

    uvicorn.run("server:app", host=args.host, port=args.port, reload=args.reload, factory=False)
