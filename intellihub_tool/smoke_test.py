import json
import os
import subprocess
import time
from pathlib import Path

import httpx
import tool  # assumes you're running this from inside intellihub_tool/

print("=== IntelliHub MCP Smoke Test ===")

# 1. Check config path
print("\n[1] Checking config path...")
config_path = Path(__file__).resolve().parent / "config" / "paths.json"
with open(config_path, "r") as f:
    cfg = json.load(f)

ai_path = cfg.get("ai_context_path")
print("Configured ai_context_path:", ai_path)

if not os.path.isdir(ai_path):
    print("❌ ERROR: ai_context_path does not exist on disk.")
else:
    print("✅ Path exists.")

# 2. Test list_files()
print("\n[2] Testing list_files()...")
files = tool.list_files()
print(f"Found {len(files)} files.")
if len(files) == 0:
    print("❌ ERROR: No files returned.")
else:
    print("Sample:", files[:5])
    print("✅ list_files() OK.")

# 3. Test read_file() on a known file
print("\n[3] Testing read_file('00_README.md')...")
try:
    content = tool.read_file("00_README.md")
    print("First 200 chars:\n", content[:200])
    print("✅ read_file() OK.")
except Exception as e:
    print("❌ ERROR:", e)

# 4. Test search()
print("\n[4] Testing search('Lumen')...")
results = tool.search("Lumen")
print(f"Found {len(results)} matches.")
if results:
    print("Sample match:", results[0])
    print("✅ search() OK.")
else:
    print("⚠️ No matches found. (May be fine depending on docs.)")

# 5. Test get_schema()
print("\n[5] Testing get_schema('seed_type')...")
try:
    schema = tool.get_schema("seed_type")
    print("First 200 chars:\n", schema[:200])
    print("✅ get_schema() OK.")
except Exception as e:
    print("❌ ERROR:", e)

# 6. Test get_module_purpose()
print("\n[6] Testing get_module_purpose('monsterseed')...")
try:
    mp = tool.get_module_purpose("monsterseed")
    print("First 200 chars:\n", mp[:200])
    print("✅ get_module_purpose() OK.")
except Exception as e:
    print("❌ ERROR:", e)

print("\n=== Smoke Test Complete ===")


print("\n[7] Testing server health check...")
server_process = None
try:
    # Start the server as a separate process
    server_process = subprocess.Popen(["python", "server.py"])
    # Give the server a moment to start
    time.sleep(2)

    # Make a request to the health check endpoint
    headers = {"Origin": "http://example.com"}
    response = httpx.get("http://127.0.0.1:8000/health", headers=headers)

    # Check the response
    if response.status_code == 200:
        print("✅ Health check status code is 200.")
    else:
        print(f"❌ ERROR: Health check status code is {response.status_code}.")

    if response.json() == {"status": "ok"}:
        print("✅ Health check response body is correct.")
    else:
        print(f"❌ ERROR: Health check response body is {response.json()}.")

    if response.headers.get("access-control-allow-origin") == "*":
        print("✅ CORS header is correct.")
    else:
        print(
            f"❌ ERROR: CORS header is {response.headers.get('access-control-allow-origin')}."
        )

except Exception as e:
    print(f"❌ ERROR: {e}")
finally:
    if server_process:
        server_process.terminate()
        server_process.wait()
        print("✅ Server process terminated.")
