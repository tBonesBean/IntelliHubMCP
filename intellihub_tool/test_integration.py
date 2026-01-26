"""
Integration test for IntelliHub MCP tool.
Tests the actual tool.py with a valid test configuration.
"""
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

def test_tool_functionality():
    """Test the tool.py functions with valid configuration."""
    print("\n=== Testing Tool Functionality ===")
    
    # Save original config
    config_path = Path(__file__).parent / "config" / "paths.json"
    config_backup = config_path.read_text()
    
    # Get absolute path to test_ai_context
    test_ai_context = Path(__file__).parent.parent / "test_ai_context"
    test_ai_context = test_ai_context.resolve()
    
    print(f"Using test ai_context: {test_ai_context}")
    
    try:
        # Update config to point to test_ai_context
        with open(config_path, "w") as f:
            json.dump({"ai_context_path": str(test_ai_context)}, f)
        
        # Unload tool module if it was already imported
        if 'tool' in sys.modules:
            del sys.modules['tool']
        
        # Import tool (this will validate config on import)
        import tool
        
        print("\n✅ PASS: Module imported successfully with valid config")
        
        # Test list_files()
        print("\nTest: list_files()")
        files = tool.list_files()
        print(f"  Found {len(files)} files")
        if len(files) > 0:
            print(f"  Sample files: {files[:3]}")
            print("✅ PASS: list_files() works")
        else:
            print("❌ FAIL: No files found")
        
        # Test read_file()
        print("\nTest: read_file('00_README.md')")
        try:
            content = tool.read_file("00_README.md")
            if "Test AI Context" in content:
                print("✅ PASS: read_file() works correctly")
            else:
                print(f"❌ FAIL: Unexpected content: {content[:50]}")
        except Exception as e:
            print(f"❌ FAIL: {e}")
        
        # Test path traversal protection
        print("\nTest: Path traversal protection")
        try:
            tool.read_file("../../etc/passwd")
            print("❌ FAIL: Path traversal was not blocked!")
        except ValueError as e:
            if "outside ai_context directory" in str(e):
                print(f"✅ PASS: Path traversal blocked")
            else:
                print(f"❌ FAIL: Wrong error: {e}")
        
        # Test search()
        print("\nTest: search('Test')")
        results = tool.search("Test")
        print(f"  Found {len(results)} matches")
        if len(results) > 0:
            print(f"  Sample result: {results[0]}")
            print("✅ PASS: search() works")
        else:
            print("⚠️  WARNING: No matches found (may be OK)")
        
        # Test diagnose()
        print("\nTest: diagnose()")
        report = tool.diagnose()
        print(f"  Status: {report['status']}")
        print(f"  Path valid: {report['path_valid']}")
        print(f"  Total files: {report['file_inventory']['total_files']}")
        print(f"  Issues: {report['issues']}")
        
        # Validate report structure
        required_keys = ["path_valid", "file_inventory", "schemas", "module_purposes", "search_index", "issues", "status"]
        missing_keys = [k for k in required_keys if k not in report]
        
        if missing_keys:
            print(f"❌ FAIL: Missing keys in report: {missing_keys}")
        else:
            print("✅ PASS: diagnose() returns complete report")
        
        # Check that issues list works correctly
        if isinstance(report["issues"], list):
            print("✅ PASS: issues is a list")
        else:
            print(f"❌ FAIL: issues is not a list: {type(report['issues'])}")
        
        # Check status determination
        if report["status"] in ["healthy", "warning", "error", "unknown"]:
            print(f"✅ PASS: Status is valid: {report['status']}")
        else:
            print(f"❌ FAIL: Invalid status: {report['status']}")
        
    finally:
        # Restore original config
        with open(config_path, "w") as f:
            f.write(config_backup)
        
        # Unload tool module
        if 'tool' in sys.modules:
            del sys.modules['tool']

def test_config_error_handling():
    """Test that tool.py handles configuration errors correctly."""
    print("\n=== Testing Config Error Handling ===")
    
    config_path = Path(__file__).parent / "config" / "paths.json"
    config_backup = config_path.read_text()
    
    try:
        # Test 1: Invalid JSON
        print("\nTest: Invalid JSON in config")
        with open(config_path, "w") as f:
            f.write("{invalid json")
        
        if 'tool' in sys.modules:
            del sys.modules['tool']
        
        try:
            import tool
            print("❌ FAIL: Should have raised RuntimeError for invalid JSON")
        except RuntimeError as e:
            if "Invalid JSON" in str(e):
                print(f"✅ PASS: Caught invalid JSON error")
            else:
                print(f"⚠️  WARNING: Got RuntimeError but wrong message: {e}")
        
        # Test 2: Missing ai_context_path key
        print("\nTest: Missing ai_context_path key")
        with open(config_path, "w") as f:
            json.dump({"wrong_key": "value"}, f)
        
        if 'tool' in sys.modules:
            del sys.modules['tool']
        
        try:
            import tool
            print("❌ FAIL: Should have raised RuntimeError for missing key")
        except RuntimeError as e:
            if "ai_context_path" in str(e):
                print(f"✅ PASS: Caught missing key error")
            else:
                print(f"⚠️  WARNING: Got RuntimeError but wrong message: {e}")
        
        # Test 3: Non-existent path
        print("\nTest: Non-existent ai_context path")
        with open(config_path, "w") as f:
            json.dump({"ai_context_path": "/nonexistent/path/to/ai_context"}, f)
        
        if 'tool' in sys.modules:
            del sys.modules['tool']
        
        try:
            import tool
            print("❌ FAIL: Should have raised RuntimeError for non-existent path")
        except RuntimeError as e:
            if "does not exist" in str(e):
                print(f"✅ PASS: Caught non-existent path error")
            else:
                print(f"⚠️  WARNING: Got RuntimeError but wrong message: {e}")
        
    finally:
        # Restore original config
        with open(config_path, "w") as f:
            f.write(config_backup)
        
        if 'tool' in sys.modules:
            del sys.modules['tool']

if __name__ == "__main__":
    print("=" * 60)
    print("IntelliHub MCP Integration Tests")
    print("=" * 60)
    
    test_tool_functionality()
    test_config_error_handling()
    
    print("\n" + "=" * 60)
    print("Tests Complete")
    print("=" * 60)
