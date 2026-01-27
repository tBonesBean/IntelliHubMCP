import os
import json
from pathlib import Path

# Load config relative to this file so CWD doesn't matter.
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config" / "paths.json"

# Validate config file exists
if not CONFIG_PATH.exists():
    raise RuntimeError(
        f"Configuration file not found: {CONFIG_PATH}\n"
        f"Please create it with the following structure:\n"
        f'{{"ai_context_path": "/path/to/your/ai_context"}}'
    )

# Load and validate config
try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
except json.JSONDecodeError as e:
    raise RuntimeError(f"Invalid JSON in configuration file {CONFIG_PATH}: {e}")
except Exception as e:
    raise RuntimeError(f"Error reading configuration file {CONFIG_PATH}: {e}")

# Validate required key exists
if "ai_context_path" not in CONFIG:
    raise RuntimeError(
        f"Missing required 'ai_context_path' key in {CONFIG_PATH}\n"
        f"Configuration must include: {{'ai_context_path': '/path/to/your/ai_context'}}"
    )

AI_CONTEXT = CONFIG["ai_context_path"]

# Validate ai_context path exists and is a directory
if not os.path.exists(AI_CONTEXT):
    raise RuntimeError(
        f"The ai_context path specified in configuration does not exist: {AI_CONTEXT}\n"
        f"Please update {CONFIG_PATH} with a valid path."
    )

if not os.path.isdir(AI_CONTEXT):
    raise RuntimeError(
        f"The ai_context path is not a directory: {AI_CONTEXT}\n"
        f"Please update {CONFIG_PATH} with a valid directory path."
    )


def list_files():
    """Return a list of all files in ai_context."""
    file_list = []
    for root, _, files in os.walk(AI_CONTEXT):
        for f in files:
            rel_path = os.path.relpath(os.path.join(root, f), AI_CONTEXT)
            file_list.append(rel_path.replace("\\", "/"))
    return file_list


def read_file(path):
    """
    Return the contents of a file relative to ai_context.

    Args:
        path: Relative path to the file within ai_context

    Returns:
        File contents as string

    Raises:
        ValueError: If path attempts to escape ai_context directory
        FileNotFoundError: If file doesn't exist
    """
    # Security: Prevent directory traversal attacks
    # Use realpath to resolve symlinks and normalize paths
    full_path = os.path.realpath(os.path.join(AI_CONTEXT, path))
    ai_context_abs = os.path.realpath(AI_CONTEXT)

    # Ensure the resolved path is within ai_context (with proper separator check)
    if not (
        full_path == ai_context_abs or full_path.startswith(ai_context_abs + os.sep)
    ):
        raise ValueError(
            f"Access denied: path '{path}' is outside ai_context directory"
        )

    # Validate file exists and is a file
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: {path}")

    if not os.path.isfile(full_path):
        raise ValueError(f"Not a file: {path}")

    # Read with error handling
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        raise ValueError(f"File is not valid UTF-8: {path}")


def search(query):
    """Search all Markdown files for a query string."""
    results = []
    for root, _, files in os.walk(AI_CONTEXT):
        for f in files:
            if not f.endswith(".md"):
                continue
            rel_path = os.path.relpath(os.path.join(root, f), AI_CONTEXT)
            with open(os.path.join(root, f), "r", encoding="utf-8") as file:
                for i, line in enumerate(file.readlines(), start=1):
                    if query.lower() in line.lower():
                        results.append(
                            {
                                "file": rel_path.replace("\\", "/"),
                                "line": i,
                                "snippet": line.strip(),
                            }
                        )
    return results


def get_schema(name):
    """Return a schema file from schemas/."""
    path = f"schemas/{name}_schema.md"
    return read_file(path)


def get_module_purpose(name):
    """Return a module purpose file from module_purposes/."""
    path = f"module_purposes/{name}.md"
    return read_file(path)


def diagnose():
    """
    Perform a full health check of the ai_context knowledge capsule.
    Returns a structured diagnostic report describing:
    - path validity
    - file inventory
    - schema health
    - module purpose health
    - search index health
    - overall status
    """

    report = {
        "path_valid": False,
        "file_inventory": {},
        "schemas": {},
        "module_purposes": {},
        "search_index": {},
        "issues": [],
        "status": "unknown",
    }

    # ------------------------------------------------------------
    # 1. PATH VALIDITY
    # ------------------------------------------------------------
    if not os.path.isdir(AI_CONTEXT):
        report["path_valid"] = False
        report["status"] = "error"
        report["issues"].append(f"ai_context path does not exist: {AI_CONTEXT}")
        return report

    report["path_valid"] = True

    # ------------------------------------------------------------
    # 2. FILE INVENTORY
    # ------------------------------------------------------------
    all_files = list_files()
    md_files = [f for f in all_files if f.endswith(".md")]

    report["file_inventory"] = {
        "total_files": len(all_files),
        "markdown_files": len(md_files),
        "has_root_readme": "00_README.md" in all_files,
        "missing_expected": [],
    }

    # Expected core files (customize as needed)
    expected_core = [
        "00_README.md",
        "architecture_overview.md",
        "design_bible.md",
        "lore_core.md",
        "naming_conventions.md",
    ]

    for expected in expected_core:
        if expected not in all_files:
            report["file_inventory"]["missing_expected"].append(expected)
            report["issues"].append(f"Missing expected file: {expected}")

    # ------------------------------------------------------------
    # 3. SCHEMA HEALTH
    # ------------------------------------------------------------
    schemas_dir = os.path.join(AI_CONTEXT, "schemas")
    schema_files = []
    unreadable_schemas = []

    if os.path.isdir(schemas_dir):
        for f in os.listdir(schemas_dir):
            if f.endswith("_schema.md"):
                schema_files.append(f)
                try:
                    # Test readability
                    read_file(f"schemas/{f}")
                except Exception as e:
                    unreadable_schemas.append(f)
                    report["issues"].append(f"Unreadable schema: {f} ({str(e)})")

    report["schemas"] = {
        "exists": os.path.isdir(schemas_dir),
        "count": len(schema_files),
        "unreadable": unreadable_schemas,
    }

    if not os.path.isdir(schemas_dir):
        report["issues"].append("schemas/ directory not found")

    # ------------------------------------------------------------
    # 4. MODULE PURPOSE HEALTH
    # ------------------------------------------------------------
    module_purposes_dir = os.path.join(AI_CONTEXT, "module_purposes")
    module_files = []
    unreadable_modules = []

    if os.path.isdir(module_purposes_dir):
        for f in os.listdir(module_purposes_dir):
            if f.endswith(".md"):
                module_files.append(f)
                try:
                    # Test readability
                    read_file(f"module_purposes/{f}")
                except Exception as e:
                    unreadable_modules.append(f)
                    report["issues"].append(
                        f"Unreadable module purpose: {f} ({str(e)})"
                    )

    report["module_purposes"] = {
        "exists": os.path.isdir(module_purposes_dir),
        "count": len(module_files),
        "unreadable": unreadable_modules,
    }

    if not os.path.isdir(module_purposes_dir):
        report["issues"].append("module_purposes/ directory not found")

    # ------------------------------------------------------------
    # 5. SEARCH INDEX HEALTH
    # ------------------------------------------------------------
    sample_results = []
    searchable = True
    try:
        # Test search with a common term
        sample_results = search("the")[:5]  # Limit to 5 results
    except Exception as e:
        searchable = False
        report["issues"].append(f"Search functionality broken: {str(e)}")

    report["search_index"] = {
        "searchable": searchable,
        "sample_results": sample_results,
    }

    # ------------------------------------------------------------
    # 6. OVERALL STATUS
    # ------------------------------------------------------------
    if not report["issues"]:
        report["status"] = "healthy"
    elif len(report["issues"]) < 3:
        report["status"] = "warning"
    else:
        report["status"] = "error"

    return report
