import asyncio
import os
import sys
from mcp.server.stdio import stdio_server

# Add the current directory to sys.path so we can import from server
sys.path.append(os.path.dirname(__file__))

from server import mcp

async def main():
    # Run the server using stdin/stdout
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(
            read_stream,
            write_stream,
            initialization_options=mcp.create_initialization_options(),
        )

if __name__ == "__main__":
    asyncio.run(main())
