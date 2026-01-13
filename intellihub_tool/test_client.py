import asyncio
import websockets
import json

async def test_mcp():
    uri = "ws://127.0.0.1:8000/mcp"
    async with websockets.connect(uri) as websocket:
        # Example handshake message (adjust to your MCP protocol)
        handshake = {
            "type": "handshake",
            "client": "test-client",
            "version": "1.0"
        }
        await websocket.send(json.dumps(handshake))
        print("Sent handshake:", handshake)

        # Wait for server response
        response = await websocket.recv()
        print("Received:", response)

asyncio.run(test_mcp())