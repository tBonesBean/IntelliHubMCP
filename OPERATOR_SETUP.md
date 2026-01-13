# IntelliHub MCP – Operator Checklist

Human‑friendly steps to start the server and confirm agents (ChatGPT/Gemini/Copilot, etc.) can reach it.

## One‑time setup

- From `intellihub_tool/`, create/activate your venv.
- Install deps: `pip install -r requirements.txt`.
- Ensure `config/paths.json` points to your local `ai_context` folder.

## Start the server

- From `intellihub_tool/` run:  
  `python server.py --host 127.0.0.1 --port 8000 --reload`
- If 8000 is busy, choose another port and note it for clients.
- Leave this terminal running.

## Quick health checks

- CLI diagnostics (hits the local data):  
  `python cli.py diagnose` → expect `Status: HEALTHY`.
- WebSocket endpoint check (tests MCP handshake):  
  `python scripts/check_endpoint.py --host 127.0.0.1 --port 8000 --path /mcp`
  - On success you’ll see JSON for `initialize` and `tools/list`.
  - If you changed ports, update `--port`.

## What to tell agent clients

- WebSocket URL: `ws://127.0.0.1:8000/mcp` (swap port if different).
- WebSocket subprotocol: `mcp` (must be requested by the client).
- Manifest: `intellihub_tool/manifest.json` (name `intellihub`, version `0.2.0`).
- Supported tools: `list_files`, `read_file`, `search`, `get_schema`, `get_module_purpose`, `diagnose`.

## If something fails

- Port conflict: rerun server on a free port (`--port 8001`), rerun the check script with the new port, and share the new URL.
- Path issue: fix `config/paths.json` to the correct `ai_context` and rerun `cli.py diagnose`.
- Missing deps: rerun `pip install -r requirements.txt`.
