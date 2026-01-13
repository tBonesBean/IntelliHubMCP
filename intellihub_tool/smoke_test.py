import json
import os
import tool  # assumes you're running this from inside intellihub_tool/

print("=== IntelliHub MCP Smoke Test ===")

# 1. Check config path
print("\n[1] Checking config path...")
with open(os.path.join("config", "paths.json"), "r") as f:
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
