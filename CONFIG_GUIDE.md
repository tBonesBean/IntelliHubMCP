# Configuration Guide for IntelliHub MCP Server

This guide documents the correct configuration formats for the IntelliHub MCP Server.

## Core Configuration Files

### 1. `config/paths.json`

This file specifies the path to your `ai_context` directory.

**Format:**

```json
{
	"ai_context_path": "/path/to/your/.ai_context"
}
```

**Example (Windows):**

```json
{
	"ai_context_path": "C:/Repos/MonTamerGens/.ai_context"
}
```

**Example (Linux/Mac):**

```json
{
	"ai_context_path": "/home/user/projects/MonTamerGens/.ai_context"
}
```

**Important Notes:**

- ❌ Do NOT add wildcards or trailing slashes: `"C:/path/*"` or `"C:/path/"`
- ✅ Use forward slashes even on Windows: `"C:/path"` (not `"C:\path"`)
- The path should point to the directory itself, not a glob pattern

---

### 2. `config.json`

Configuration for MCP server launcher.

**Format:**

```json
{
	"mcpServers": {
		"intellihub": {
			"type": "mcp",
			"manifestPath": "./manifest.json",
			"command": "python",
			"args": ["./server.py", "--host", "localhost", "--port", "8002"]
		}
	}
}
```

**Valid Server Arguments:**

- `--host <hostname>` - Host to bind (default: 127.0.0.1)
- `--port <port>` - Port to bind (default: 8000)
- `--reload` - Enable auto-reload during development

**Important Notes:**

- ❌ Do NOT use `--mcp` flag (does not exist)
- ✅ Paths in `args` are relative to the `intellihub_tool/` directory
- ✅ Use `./server.py` (relative) or absolute path

---

### 3. `.vscode/mcp.json`

Configuration for VS Code Claude extension.

**Stdio Server Format:**

```json
{
	"servers": {
		"intellihub_stdio": {
			"type": "stdio",
			"command": "python",
			"args": ["stdio_server.py"]
		}
	},
	"inputs": []
}
```

**Important Notes for stdio_server.py:**

- ❌ stdio_server.py does NOT accept any command-line arguments
- ❌ Do NOT use `--host`, `--port`, or `--mcp` flags with stdio_server.py
- ✅ Use `python` (not `python.exe`) for portability
- ✅ Use relative path `stdio_server.py` when running from `intellihub_tool/` directory
- ✅ Use absolute path if running from elsewhere

**Example with absolute path:**

```json
{
	"servers": {
		"intellihub_stdio": {
			"type": "stdio",
			"command": "python",
			"args": ["C:/Services/intellihub_tool/stdio_server.py"]
		}
	},
	"inputs": []
}
```

---

## Server Types

### WebSocket Server (`server.py`)

**Start Command:**

```pwsh
python server.py --host 127.0.0.1 --port 8000 --reload
```

**Valid Arguments:**

- `--host HOST` - Bind to specific host (default: 127.0.0.1)
- `--port PORT` - Bind to specific port (default: 8000)
- `--reload` - Enable auto-reload (development mode)

**Client Connection:**

- WebSocket URL: `ws://127.0.0.1:8000/mcp`
- WebSocket subprotocol: `mcp`
- Health check: `http://127.0.0.1:8000/health`

---

### Stdio Server (`stdio_server.py`)

**Start Command:**

```pwsh
python stdio_server.py
```

**Valid Arguments:**

- None - stdio_server.py does not accept command-line arguments

**Client Connection:**

- Communicates via stdin/stdout
- Used by Claude Desktop and similar stdio-based MCP clients

---

## Common Configuration Mistakes

### ❌ WRONG Examples

```json
// config/paths.json - DO NOT USE
{
	"ai_context_path": "C:/path/*" // ❌ No wildcards
}
```

```json
// .vscode/mcp.json - DO NOT USE
{
	"servers": {
		"intellihub_stdio": {
			"type": "stdio",
			"command": "python.exe", // ❌ Not portable
			"args": [
				"C:\\absolute\\windows\\path\\stdio_server.py", // ❌ Hardcoded
				"--host",
				"localhost", // ❌ stdio doesn't accept arguments
				"--port",
				"8002", // ❌ stdio doesn't accept arguments
				"--mcp" // ❌ Flag doesn't exist
			]
		}
	}
}
```

```json
// config.json - DO NOT USE
{
	"mcpServers": {
		"intellihub": {
			"command": "python",
			"args": ["./server.py", "--host", "localhost", "--port", "8002", "--mcp"]
			// ❌ --mcp flag doesn't exist
		}
	}
}
```

---

### ✅ CORRECT Examples

```json
// config/paths.json
{
	"ai_context_path": "C:/Repos/MonTamerGens/.ai_context"
}
```

```json
// .vscode/mcp.json
{
	"servers": {
		"intellihub_stdio": {
			"type": "stdio",
			"command": "python",
			"args": ["stdio_server.py"]
		}
	},
	"inputs": []
}
```

```json
// config.json
{
	"mcpServers": {
		"intellihub": {
			"type": "mcp",
			"manifestPath": "./manifest.json",
			"command": "python",
			"args": ["./server.py", "--host", "localhost", "--port", "8002"]
		}
	}
}
```

---

## Quick Verification

After configuring, verify your setup:

1. **Test path configuration:**

    ```pwsh
    cd intellihub_tool
    python cli.py diagnose
    ```

    Should show: `Status: HEALTHY`

2. **Test WebSocket server:**

    ```pwsh
    cd intellihub_tool
    python server.py --host 127.0.0.1 --port 8000
    ```

    Then in another terminal:

    ```pwsh
    python scripts/check_endpoint.py --host 127.0.0.1 --port 8000 --path /mcp
    ```

3. **Test stdio server:**

    ```pwsh
    cd intellihub_tool
    echo '{"jsonrpc":"2.0","method":"initialize","id":1,"params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | python stdio_server.py --log-level debug
    ```

---

## Need Help?

- Check `OPERATOR_SETUP.md` for operator-friendly setup instructions
- Check `AGENT_USAGE.md` for agent integration guidelines
- Check `README.md` for general project information
