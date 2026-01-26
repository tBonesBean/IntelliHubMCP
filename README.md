# **IntelliHub MCP Tool**

The IntelliHub MCP Tool exposes the MonTamerGens `/ai_context/` directory as a structured, read‑only knowledge capsule for AI agents. It provides a consistent interface for retrieving architecture documents, lore, schemas, naming conventions, and module responsibilities — enabling agents to reason over the project using canonical, up‑to‑date information.

This tool is intentionally minimal: it does not modify files, generate content, or access code outside the curated IntelliHub. Its purpose is clarity, stability, and safe knowledge retrieval.

---

## **Purpose**

The IntelliHub serves as the authoritative source of truth for MonTamerGens. This MCP tool allows AI agents to:

- read documentation directly from the project  
- understand system architecture and design pillars  
- reference schemas and data contracts  
- inspect module responsibilities  
- search across the knowledge base  

By exposing these documents through a stable interface, the tool ensures that agents operate with accurate, consistent context.

---

## **Folder Layout**

```
intellihub_tool/
├── manifest.json        # MCP tool definition
├── tool.py              # Function implementations
├── server.py            # SSE/WebSocket server implementation
├── stdio_server.py      # Stdio server implementation
├── README.md            # This file
└── config/
    └── paths.json       # Points to your /ai_context/ directory
```

---

## **Functions**

### `list_files()`
Returns all files in the ai_context directory.

### `read_file(path)`
Reads a Markdown file using a relative path.

### `search(query)`
Searches across all documentation for a keyword or phrase.

### `get_schema(name)`
Returns a schema file from `/schemas/`.

### `get_module_purpose(name)`
Returns a module documentation file from `/module_purposes/`.

### `diagnose()`
Performs a full health check of the IntelliHub knowledge capsule, verifying paths, files, schemas, and search index.

---

## **Example Usage**

### List all documentation files
```
list_files()
```

### Read the core lore document
```
read_file("lore_core.md")
```

### Search for references to “Lumen”
```
search("Lumen")
```

### Fetch the mutagen schema
```
get_schema("mutagen")
```

### Retrieve the monsterseed module description
```
get_module_purpose("monsterseed")
```

### Check the health of the IntelliHub
```
diagnose()
```

---

## **Configuration**

The tool reads its base path from:

```
config/paths.json
```

Example:

```json
{
  "ai_context_path": "D:/Projects/MonTamerGens/docs/ai_context"
}
```

This allows the tool to be portable across machines and directory layouts.

---

## **Limitations**

- The tool is **read-only**.  
- It only exposes files inside `/ai_context/`.  
- It does not execute code or modify project state.  

These constraints ensure safety, stability, and predictable behavior.

---

## **Local Setup & Server**

1. Create/activate a virtualenv in `intellihub_tool/`.
2. Install deps: `pip install -r requirements.txt`.
3. Run the MCP server: `python server.py --host 127.0.0.1 --port 8000 --reload`.
4. WebSocket endpoint lives at `/mcp` (e.g., `ws://127.0.0.1:8000/mcp`).
5. CLI diagnostics (from `intellihub_tool/`): `python cli.py diagnose`.

### **Stdio Server**

For clients that support stdio communication (like Claude Desktop):
- Command: `python`
- Args: `stdio_server.py` (or use absolute path if running from outside the intellihub_tool directory)

> Ensure `config/paths.json` points to your local `ai_context` root.

## **Agent Integration**

- WebSocket URL: `ws://127.0.0.1:8000/mcp` (adjust host/port as needed).
- WebSocket subprotocol: `mcp`.
- Manifest: `intellihub_tool/manifest.json` (name: `intellihub`, version: `0.2.0`).
- Quick endpoint check (from `intellihub_tool/`): `python scripts/check_endpoint.py --host 127.0.0.1 --port 8000 --path /mcp`.
- On success you should see JSON-RPC responses for `initialize` and `tools/list`.
