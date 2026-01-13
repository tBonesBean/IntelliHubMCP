import os
import json
from pathlib import Path

import utils

# Load config relative to this file so CWD doesn't matter.
BASE_DIR = Path(__file__).resolve().parent
with open(BASE_DIR / "config" / "paths.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

AI_CONTEXT = CONFIG["ai_context_path"]


def list_files():
    """Return a list of all files in ai_context."""
    file_list = []
    for root, _, files in os.walk(AI_CONTEXT):
        for f in files:
            rel_path = os.path.relpath(os.path.join(root, f), AI_CONTEXT)
            file_list.append(rel_path.replace("\\", "/"))
    return file_list


def read_file(path):
    """Return the contents of a file relative to ai_context."""
    full_path = os.path.join(AI_CONTEXT, path)
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


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
        "status": "unknown",
    }

    # ------------------------------------------------------------
    # 1. PATH VALIDITY
    # ------------------------------------------------------------
    if not os.path.isdir(AI_CONTEXT):
        report["path_valid"] = False
        report["status"] = "error"
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

    for f in expected_core:
        if f not in all_files:
            report["file_inventory"]["missing_expected"].append(f)

    # ------------------------------------------------------------
    # 3. SCHEMA HEALTH
    # ------------------------------------------------------------
    schema_dir = os.path.join(AI_CONTEXT, "schemas")
    schema_report = {
        "exists": os.path.isdir(schema_dir),
        "count": 0,
        "files": [],
        "unreadable": [],
    }

    if schema_report["exists"]:
        for f in os.listdir(schema_dir):
            if f.endswith(".md"):
                schema_report["files"].append(f)
                try:
                    read_file(f"schemas/{f}")
                except Exception:
                    schema_report["unreadable"].append(f)

        schema_report["count"] = len(schema_report["files"])

    report["schemas"] = schema_report

    # ------------------------------------------------------------
    # 4. MODULE PURPOSE HEALTH
    # ------------------------------------------------------------
    mp_dir = os.path.join(AI_CONTEXT, "module_purposes")
    mp_report = {
        "exists": os.path.isdir(mp_dir),
        "count": 0,
        "files": [],
        "unreadable": [],
    }

    if mp_report["exists"]:
        for f in os.listdir(mp_dir):
            if f.endswith(".md"):
                mp_report["files"].append(f)
                try:
                    read_file(f"module_purposes/{f}")
                except Exception:
                    mp_report["unreadable"].append(f)

        mp_report["count"] = len(mp_report["files"])

    report["module_purposes"] = mp_report

    # ------------------------------------------------------------
    # 5. SEARCH INDEX HEALTH
    # ------------------------------------------------------------
    search_test = search("the")  # harmless, common token
    report["search_index"] = {
        "searchable": isinstance(search_test, list),
        "sample_results": search_test[:3] if isinstance(search_test, list) else [],
    }

    # ------------------------------------------------------------
    # 6. SUMMARY STATUS
    # ------------------------------------------------------------
    issues = []

    if not report["path_valid"]:
        issues.append("invalid_path")

    if report["file_inventory"]["missing_expected"]:
        issues.append("missing_expected_files")

    if report["schemas"]["unreadable"]:
        issues.append("unreadable_schemas")

    if report["module_purposes"]["unreadable"]:
        issues.append("unreadable_module_purposes")

    if not report["search_index"]["searchable"]:
        issues.append("search_failure")

    report["status"] = "healthy" if not issues else "issues_detected"
    report["issues"] = issues

    return report
