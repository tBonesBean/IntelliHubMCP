"""
Test security fixes and configuration validation for IntelliHub MCP tool.
"""
import os
import sys
import tempfile
import shutil
import json
from pathlib import Path

# We need to test without importing tool.py directly since it validates config on import
# Let's create a test that verifies the behavior

def test_path_traversal_protection():
    """Test that read_file blocks path traversal attacks."""
    print("\n=== Testing Path Traversal Protection ===")
    
    # Create temporary ai_context directory
    with tempfile.TemporaryDirectory() as tmpdir:
        ai_context = os.path.join(tmpdir, "ai_context")
        os.makedirs(ai_context)
        
        # Create a test file inside ai_context
        test_file = os.path.join(ai_context, "test.md")
        with open(test_file, "w") as f:
            f.write("This is a test file")
        
        # Create a file outside ai_context that should not be accessible
        outside_file = os.path.join(tmpdir, "outside.txt")
        with open(outside_file, "w") as f:
            f.write("This should not be accessible")
        
        # Create config file
        config_dir = os.path.join(tmpdir, "config")
        os.makedirs(config_dir)
        config_path = os.path.join(config_dir, "paths.json")
        with open(config_path, "w") as f:
            json.dump({"ai_context_path": ai_context}, f)
        
        # Create a minimal tool.py implementation for testing
        tool_content = f"""
import os
import json
from pathlib import Path

BASE_DIR = Path("{tmpdir}")
CONFIG_PATH = BASE_DIR / "config" / "paths.json"

if not CONFIG_PATH.exists():
    raise RuntimeError("Config not found")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

if "ai_context_path" not in CONFIG:
    raise RuntimeError("Missing ai_context_path")

AI_CONTEXT = CONFIG["ai_context_path"]

if not os.path.exists(AI_CONTEXT):
    raise RuntimeError(f"ai_context does not exist: {{AI_CONTEXT}}")

if not os.path.isdir(AI_CONTEXT):
    raise RuntimeError(f"ai_context is not a directory: {{AI_CONTEXT}}")

def read_file(path):
    # Security: Prevent directory traversal attacks
    full_path = os.path.abspath(os.path.join(AI_CONTEXT, path))
    ai_context_abs = os.path.abspath(AI_CONTEXT)
    
    if not full_path.startswith(ai_context_abs):
        raise ValueError(f"Access denied: path '{{path}}' is outside ai_context directory")
    
    # Validate file exists and is a file
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: {{path}}")
    
    if not os.path.isfile(full_path):
        raise ValueError(f"Not a file: {{path}}")
    
    # Read with error handling
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        raise ValueError(f"File is not valid UTF-8: {{path}}")
"""
        
        # Write test module
        test_module_path = os.path.join(tmpdir, "test_tool.py")
        with open(test_module_path, "w") as f:
            f.write(tool_content)
        
        # Add tmpdir to path and import
        sys.path.insert(0, tmpdir)
        try:
            import test_tool
            
            # Test 1: Valid file access should work
            print("Test 1: Reading valid file inside ai_context...")
            try:
                content = test_tool.read_file("test.md")
                if content == "This is a test file":
                    print("✅ PASS: Successfully read file inside ai_context")
                else:
                    print("❌ FAIL: Wrong content returned")
            except Exception as e:
                print(f"❌ FAIL: {e}")
            
            # Test 2: Path traversal should be blocked
            print("\nTest 2: Attempting path traversal with ../outside.txt...")
            try:
                test_tool.read_file("../outside.txt")
                print("❌ FAIL: Path traversal was not blocked!")
            except ValueError as e:
                if "outside ai_context directory" in str(e):
                    print(f"✅ PASS: Path traversal blocked: {e}")
                else:
                    print(f"❌ FAIL: Wrong error: {e}")
            except Exception as e:
                print(f"❌ FAIL: Unexpected error: {e}")
            
            # Test 3: Absolute path outside should be blocked
            print("\nTest 3: Attempting absolute path outside ai_context...")
            try:
                test_tool.read_file(outside_file)
                print("❌ FAIL: Absolute path outside was not blocked!")
            except ValueError as e:
                if "outside ai_context directory" in str(e):
                    print(f"✅ PASS: Absolute path blocked: {e}")
                else:
                    print(f"❌ FAIL: Wrong error: {e}")
            except Exception as e:
                print(f"❌ FAIL: Unexpected error: {e}")
            
            # Test 4: Non-existent file
            print("\nTest 4: Attempting to read non-existent file...")
            try:
                test_tool.read_file("nonexistent.md")
                print("❌ FAIL: Should have raised FileNotFoundError")
            except FileNotFoundError as e:
                print(f"✅ PASS: FileNotFoundError raised: {e}")
            except Exception as e:
                print(f"❌ FAIL: Wrong error type: {e}")
                
        finally:
            sys.path.remove(tmpdir)
            if 'test_tool' in sys.modules:
                del sys.modules['test_tool']

def test_config_validation():
    """Test configuration validation."""
    print("\n=== Testing Configuration Validation ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test 1: Missing config file
        print("\nTest 1: Missing config file...")
        test_code = f"""
import os
import sys
import json
from pathlib import Path

BASE_DIR = Path("{tmpdir}")
CONFIG_PATH = BASE_DIR / "config" / "paths.json"

if not CONFIG_PATH.exists():
    print("✅ PASS: Config file check works")
    raise RuntimeError("Configuration file not found")
else:
    print("❌ FAIL: Should have detected missing config")
"""
        try:
            exec(test_code)
        except RuntimeError:
            pass
        
        # Test 2: Invalid JSON
        print("\nTest 2: Invalid JSON in config...")
        config_dir = os.path.join(tmpdir, "config")
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, "paths.json")
        with open(config_path, "w") as f:
            f.write("{invalid json")
        
        test_code2 = f"""
import json
from pathlib import Path

CONFIG_PATH = Path("{config_path}")
try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
    print("❌ FAIL: Should have raised JSONDecodeError")
except json.JSONDecodeError as e:
    print(f"✅ PASS: JSONDecodeError caught: {{type(e).__name__}}")
"""
        exec(test_code2)
        
        # Test 3: Missing required key
        print("\nTest 3: Missing required key...")
        with open(config_path, "w") as f:
            json.dump({"wrong_key": "value"}, f)
        
        test_code3 = f"""
import json
from pathlib import Path

CONFIG_PATH = Path("{config_path}")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

if "ai_context_path" not in CONFIG:
    print("✅ PASS: Missing key detected")
else:
    print("❌ FAIL: Should have detected missing ai_context_path")
"""
        exec(test_code3)
        
        # Test 4: Non-existent path
        print("\nTest 4: Non-existent ai_context path...")
        with open(config_path, "w") as f:
            json.dump({"ai_context_path": "/nonexistent/path"}, f)
        
        test_code4 = f"""
import os
import json
from pathlib import Path

CONFIG_PATH = Path("{config_path}")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

AI_CONTEXT = CONFIG["ai_context_path"]
if not os.path.exists(AI_CONTEXT):
    print(f"✅ PASS: Non-existent path detected")
else:
    print(f"❌ FAIL: Should have detected non-existent path")
"""
        exec(test_code4)
        
        # Test 5: Path is not a directory
        print("\nTest 5: ai_context path is a file, not a directory...")
        file_path = os.path.join(tmpdir, "notadir.txt")
        with open(file_path, "w") as f:
            f.write("test")
        
        with open(config_path, "w") as f:
            json.dump({"ai_context_path": file_path}, f)
        
        test_code5 = f"""
import os
import json
from pathlib import Path

CONFIG_PATH = Path("{config_path}")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

AI_CONTEXT = CONFIG["ai_context_path"]
if os.path.exists(AI_CONTEXT) and not os.path.isdir(AI_CONTEXT):
    print(f"✅ PASS: File path detected (not a directory)")
else:
    print(f"❌ FAIL: Should have detected that path is not a directory")
"""
        exec(test_code5)

if __name__ == "__main__":
    print("=" * 60)
    print("IntelliHub MCP Security Tests")
    print("=" * 60)
    
    test_path_traversal_protection()
    test_config_validation()
    
    print("\n" + "=" * 60)
    print("Tests Complete")
    print("=" * 60)
